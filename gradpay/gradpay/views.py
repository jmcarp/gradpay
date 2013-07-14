# Django imports 
from django.shortcuts import render_to_response
from django.template import RequestContext

# Import models
from models import Survey
from models import Degree

# Import forms
from forms import ResultForm
from forms import SurveyForm

import json
from django.http import HttpResponse
from django.db.models import Avg, Count
from gradpay.aggregates import Median
from django.db.models import Q

from django.conf import settings

# Set up hash regex
import re
SHA1_RE = re.compile('^[a-f0-9]{40}$')

relation_map = {
    'institution' : 'institution__name',
    'state' : 'institution__state',
    'department' : 'department__name',
}

def fmt_factory(pct, rnd):
    def fmt(num):
        if not isinstance(num, float):
            return num
        app = ''
        if pct:
            num *= 100
            app = '%'
        num = round(num, rnd)
        if rnd == 0:
            num = int(num)
        if app:
            return '%s%s' % (num, app)
        return num
    return fmt

class VarInfo(object):
    
    def __init__(self, name, type, fun=None, agg=None):
        self.name = name
        self.type = type
        self.fun = fun
        self.agg = agg

    def extract(self, row):
        val = row[self.name]
        if self.fun is not None:
            return self.fun(val)
        return val

vars = {
    'institution' : VarInfo('institution__name', 'stored'),
    'state' : VarInfo('institution__state', 'stored'),
    'state_code' : VarInfo('institution__state_code', 'stored'),
    'county_code' : VarInfo('institution__county_code', 'stored'),
    'department' : VarInfo('department__name', 'stored'),
    'stipend' : VarInfo(
        'avg_stipend', 
        'computed', 
        fmt_factory(False, 0), 
        agg=Median('stipend')
    ),
    'teaching' : VarInfo(
        'avg_teach_frac', 
        'computed', 
        fmt_factory(True, 0), 
        agg=Avg('_teaching_fraction')
    ),
    'teaching_num' : VarInfo(
        'avg_teach_frac', 
        'computed', 
        fmt_factory(False, 2), 
        agg=Avg('_teaching_fraction')
    ),
    'num_resp' : VarInfo(
        'num_resp', 
        'computed', 
        agg=Count('stipend')
    ),
}

sort_map = {
    'asc' : '',
    'desc' : '-',
}

def scatter_json(request):
    """
    """
    # Get variables
    xv = request.GET.get('xv')
    yv = request.GET.get('yv')
    grouping_variables = request.GET.get('grouping_vars', 'institution')
    grouping_variables = grouping_variables.split(',')

    # Get annotation arguments
    annotate_args = {
        vars[xv].name : vars[xv].agg,
        vars[yv].name : vars[yv].agg,
    }
    
    # 
    columns = [xv, yv] + grouping_variables

    if 'num_resp' not in annotate_args:
        annotate_args['num_resp'] = vars['num_resp'].agg
        columns.append('num_resp')
    
    # Get surveys
    rows = Survey.objects
    
    # Only look at PhD students
    # TODO: Filter by degree type
    degrees = Degree.objects
    phd_degree = degrees.filter(name__contains='PhD').get()
    rows = rows.filter(degree__in=[phd_degree])

    # Only look at activated responses
    rows = rows.filter(is_active=True)

    # Compute average stipend
    rows = rows\
        .values(*[vars[g].name for g in grouping_variables])\
        .annotate(**annotate_args)
    
    # Only show rows with minimum number of responses
    rows = rows.filter(num_resp__gte=settings.MIN_TABLE_ROWS)

    # Get aaData
    results = []
    for row in rows:
        result = {column : vars[column].extract(row)
            for column in columns
            if vars[column].name in row}
        results.append(result)

    # Serialize data to JSON
    json_data = json.dumps(results)

    # Return JSON
    return HttpResponse(json_data, mimetype='application/json')
    
def choro_json(request):
    '''Get data for choropleth.
    
    (Request) args:
        iv : Independent variable for grouping data. Should be
             'state' or 'county'
        dv : Dependent variable for aggregating data. Examples
             include stipend, teaching, num_resp
    Returns:
        HTTPResponse containing JSON data--dictionary mapping
        state / county FIPS codes to aggregated data
    
    '''
    
    # Get variables
    iv = request.GET.get('iv', 'state')
    dv = request.GET.get('dv', 'stipend')

    # Get annotation params
    annotate_args = {
        vars[dv].name : vars[dv].agg,
    }
    if 'num_resp' not in annotate_args:
        annotate_args['num_resp'] = vars['num_resp'].agg

    # Get surveys
    rows = Survey.objects
    
    # Only look at PhD students
    # TODO: Filter by degree type
    degrees = Degree.objects
    phd_degree = degrees.filter(name__contains='PhD').get()
    rows = rows.filter(degree__in=[phd_degree])

    # Only look at activated responses
    rows = rows.filter(is_active=True)

    # Compute aggregate
    rows = rows\
        .values(vars[iv].name)\
        .annotate(**annotate_args)
    
    # Only show rows with minimum number of responses
    rows = rows.filter(num_resp__gte=settings.MIN_CHORO_ROWS)

    # Build result dictionary
    result = {}
    for row in rows:
        key = vars[iv].extract(row)
        val = vars[dv].extract(row)
        result[key] = val
    
    # Serialize data to JSON
    json_data = json.dumps(result)

    # Return JSON
    return HttpResponse(json_data, mimetype='application/json')

def results_json(request):
    """Get JSON-formatted data for DataTable.

    (Request) args:
        grouping_vars : comma-separated list of grouping variables
        display_vars : comma-separated list of display variables
        sSearch : search term
        ...
    Returns:
        HTTPResponse containing JSON data for request in 
        DataTables-friendly format
    
    """
    
    # Get sEcho [datatables security param]
    sEcho = request.GET.get('sEcho', 0)

    # Get search units
    grouping_variables = request.GET.get('grouping_vars', 'institution')
    grouping_variables = grouping_variables.split(',')
    
    # Get display variables
    display_variables = request.GET.get('display_vars', 'salary')
    display_variables = display_variables.split(',')
    if not display_variables[0]:
        display_variables = [] 
    display_variables.append('num_resp')

    # Get annotation arguments
    annotate_args = {}
    for dv in display_variables:
        annotate_args[vars[dv].name] = vars[dv].agg
    
    columns = grouping_variables + display_variables

    # Get search term
    like = request.GET.get('sSearch', '')
    like_lookup = ''
    if like:
        visible_stored_vars = [vars[col] for col in columns if vars[col].type == 'stored']
        like_lookup = Q(**{visible_stored_vars[0].name + '__icontains' : like})
        for var in visible_stored_vars[1:]:
            like_lookup = like_lookup | Q(**{var.name + '__icontains' : like})
    
    # Sorting
    order_by_fields = []
    n_sort_cols = request.GET.get('iSortingCols')
    n_sort_cols = int(n_sort_cols)
    for sort_idx in range(n_sort_cols):
        sort_pos = request.GET.get('iSortCol_%d' % (sort_idx))
        sort_pos = int(sort_pos)
        sort_var = vars[columns[sort_pos]]
        sort_name = sort_var.name
        sort_dir = request.GET.get('sSortDir_%d' % (sort_idx))
        sort_sign = sort_map[sort_dir]
        order_by_fields.append('%s%s' % (sort_sign, sort_name))

    # Get offset and limit
    offset = request.GET.get('iDisplayStart', 0)
    offset = max(0, int(offset))
    limit = request.GET.get('iDisplayLength', 10)
    limit = min(int(limit), 100)
    
    # Get surveys
    rows = Survey.objects
    
    # Only look at PhD students
    # TODO: Filter by degree type
    degrees = Degree.objects
    phd_degree = degrees.filter(name__contains='PhD').get()
    rows = rows.filter(degree__in=[phd_degree])

    # Only look at activated responses
    rows = rows.filter(is_active=True)

    # Filter by search term
    if like_lookup:
        rows = rows.filter(like_lookup)

    # Compute average stipend
    rows = rows\
        .values(*[vars[g].name for g in grouping_variables])\
        .annotate(**annotate_args)
    
    # Only show rows with minimum number of responses
    rows = rows.filter(num_resp__gte=settings.MIN_TABLE_ROWS)

    # Order
    rows = rows.order_by(*order_by_fields)

    # Get total count
    count_total = rows.count()

    # Apply offset and limit
    rows = rows[offset : offset + limit]
    
    # Get aaData
    aaData = []
    for row in rows:
        aaData.append([vars[col].extract(row) for col in columns if vars[col].name in row])

    # Assemble data
    data = {
        'sEcho' : sEcho,
        'iTotalRecords' : count_total,
        'iTotalDisplayRecords' : count_total,
        'aaData' : aaData,
    }
    
    # Serialize data to JSON
    json_data = json.dumps(data)

    # Return JSON
    return HttpResponse(json_data, mimetype='application/json')

def channel(request):
    
    return render_to_response('social/facebook-channel.html')

def home(request):
    
    # Get data counts
    surveys = Survey.objects.filter(is_active=True)
    context = {
        'n_resp' : surveys.count(),
        'n_inst' : surveys.values('institution').annotate(Count('stipend')).count(),
        'n_dept' : surveys.values('department').annotate(Count('stipend')).count(),
    }

    return render_to_response('home.html', context, context_instance=RequestContext(request))

def linkedinfo(request):
    
    return render_to_response('linkedinfo.html', context_instance=RequestContext(request))

def about(request):
    
    return render_to_response('about.html', context_instance=RequestContext(request))

def faq(request):
    
    return render_to_response('faq.html', context_instance=RequestContext(request))

def get_stipends(request):
    
    # Get stipends from database
    stipends = Survey.objects.filter(is_active=True).values('stipend')
    stipends = [stipend['stipend'] for stipend in stipends]
    stipends_json = json.dumps(stipends)
    
    # Return JSON
    return HttpResponse(stipends_json, mimetype='application/json')

def results_figure(request):
    
    return render_to_response('hist.html', context_instance=RequestContext(request))

def results_scatter(request):

    return render_to_response('scatter.html', context_instance=RequestContext(request))

def results_choro(request):

    return render_to_response('choro.html', context_instance=RequestContext(request))

def results_table(request):
    
    result_form = ResultForm()
    return render_to_response(
        'results.html', 
        {
            'skip_fluid' : True, 
            'form' : result_form
        }, 
        context_instance=RequestContext(request)
    )

def contact(request):

    return render_to_response('contact.html', context_instance=RequestContext(request))

def activate(request, key):
    
    # Default status is failure
    status = 'failure'
    
    # Skip unless key matches hash pattern
    if SHA1_RE.search(key):

        try:
            
            # Find survey
            survey = Survey.objects.get(activation_key=key)

            # Delete users w/ same email
            Survey.objects.\
                filter(email=survey.email).\
                exclude(activation_key=key).\
                delete()

            # Activate target survey
            survey.is_active = True
            survey.activation_key = 'ACTIVATED'
            survey.save()

            # Success
            status = 'success'
        
        # Couldn't find survey
        except Survey.DoesNotExist:
            
            pass

    # Return response
    return render_to_response(
        'activation_complete.html', 
        {'status' : status},
        context_instance=RequestContext(request)
    )

def survey(request):

    # Save data or display form
    if request.method == 'POST':
        survey_form = SurveyForm(request.POST)
        if survey_form.is_valid():
            survey_form.save()
            # Redirect
            return render_to_response('survey_complete.html', context_instance=RequestContext(request))
    else:
        survey_form = SurveyForm()

    # Display form
    return render_to_response('survey.html', {'form' : survey_form}, RequestContext(request))
