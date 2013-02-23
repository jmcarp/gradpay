# 
from django.shortcuts import render_to_response
from django.template import RequestContext

# Import models
from models import Survey
from forms import ResultForm, SurveyForm

import json
from django.http import HttpResponse
from django.db.models import Avg, Count
from django.db.models import Q

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
    return '%s%s' % (num, app)
  return fmt

#def row_extract(row, var):
#  if 'fun' in var:
#    return var['fun'](row[var['name']])
#  return row[var['name']]
#def row_extract(row, var):
#  if isinstance(var, tuple):
#    return var[1](row[var[0]])
#  return row[var]

def var_name(var):
  if isinstance(var, tuple):
    return var[0]
  return var

class VarInfo(object):
  
  def __init__(self, name, type, fun=None):
    self.name = name
    self.type = type
    self.fun = fun

  def extract(self, row):
    val = row[self.name]
    if self.fun is not None:
      return self.fun(val)
    return val

vars = {
  'institution' : VarInfo('institution__name', 'stored'),
  'state' : VarInfo('institution__state', 'stored'),
  'department' : VarInfo('department__name', 'stored'),
  'avg_stipend' : VarInfo('avg_stipend', 'computed', fmt_factory(False, 0)),
  'avg_teach_frac' : VarInfo('avg_teach_frac', 'computed', fmt_factory(True, 0)),
  'num_resp' : VarInfo('num_resp', 'computed'),
}
"""
vars = {
  'institution' : {
    'name' : 'institution__name',
    'type' : 'stored',
  },
  'state' : {
    'name' : 'institution__state',
    'type' : 'stored',
  },
  'department' : {
    'name' : 'department__name',
    'type' : 'stored',
  },
  'avg_stipend' : {
    'name' : 'avg_stipend',
    'type' : 'computed',
    'fun' : fmt_factory(False, 0),
  },
  'avg_teach_frac' : {
    'name' : 'avg_teach_frac',
    'type' : 'computed',
    'fun' : fmt_factory(True, 0),
  },
  'num_resp' : {
    'name' : 'num_resp',
    'type' : 'computed',
  },
}
"""
#stored_vars = [
#  'institution__name',
#  'institution__state',
#  'department__name',
#]
#computed_vars = [
#  ('avg_stipend', fmt_factory(False, 0)),
#  ('avg_teach_frac', fmt_factory(True, 0)),
#  'num_resp',
#]
#vars = stored_vars + computed_vars

sort_map = {
  'asc' : '',
  'desc' : '-',
}

annotate_map = {
  'avg_stipend'    : Avg('stipend'), 
  'avg_teach_frac' : Avg('_teaching_fraction'), 
  'num_resp'       : Count('stipend'),
}
def results_json(request):
  
  # Get sEcho [datatables security param]
  sEcho = request.GET.get('sEcho', 0)

  # Get search units
  grouping_variables = request.GET.get('grouping_vars', 'institution')
  grouping_variables = grouping_variables.split(',')
  #units = request.GET.get('units', 'institution')
  #units = units.split(',')
  #units = [relation_map[unit] for unit in units if unit in relation_map]
  
  # Get display variables
  display_variables = request.GET.get('display_vars', 'salary')
  display_variables = display_variables.split(',')
  if not display_variables[0]:
    display_variables = [] 
  display_variables.append('num_resp')
  annotate_args = {}
  for dv in display_variables:
    annotate_args[dv] = annotate_map[dv]
  
  columns = grouping_variables + display_variables

  # Get search term
  like = request.GET.get('sSearch', '')
  like_lookup = ''
  if like:
    visible_stored_vars = [col for col in columns if vars[col]['type'] == 'stored']
    like_lookup = Q(**{visible_stored_vars[0] + '__icontains' : like})
    for var in visible_stored_vars[1:]:
      like_lookup = like_lookup | Q(**{var + '__icontains' : like})
    #like_lookup = Q(**{stored_vars[0] + '__icontains' : like})
    #for var in stored_vars[1:]:
    #  like_lookup = like_lookup | Q(**{var + '__icontains' : like})
  
  # Sorting
  order_by_fields = []
  n_sort_cols = request.GET.get('iSortingCols')
  n_sort_cols = int(n_sort_cols)
  for sort_idx in range(n_sort_cols):
    sort_pos = request.GET.get('iSortCol_%d' % (sort_idx))
    sort_pos = int(sort_pos)
    sort_var = vars[columns[sort_pos]]
    sort_name = sort_var.name
    #sort_name = sort_var['name']
    sort_dir = request.GET.get('sSortDir_%d' % (sort_idx))
    sort_sign = sort_map[sort_dir]
    order_by_fields.append('%s%s' % (sort_sign, sort_name))

  ## Get sort variable
  #sort_col = request.GET.get('iSortCol_0', '0')
  #sort_col = int(sort_col)
  #sort_var = vars[columns[sort_col]]['name']#columns[sort_col]['name']
  ##sort_var = vars[sort_col]
  ##if isinstance(sort_var, tuple):
  ##  sort_var = sort_var[0]

  ## Get sort direction
  #sort_dir = request.GET.get('sSortDir_0', 'dsc')
  #sort_sign = sort_map[sort_dir]
  #order_by = sort_sign + sort_var

  # Get offset and limit
  offset = request.GET.get('iDisplayStart', 0)
  offset = max(0, int(offset))
  limit = request.GET.get('iDisplayLength', 10)
  limit = min(int(limit), 100)
  
  # Get surveys
  rows = Survey.objects
  
  # Only look at activated responses
  rows = rows.filter(is_active=True)

  # Filter by search term
  if like_lookup:
    rows = rows.filter(like_lookup)

  # Compute average stipend
  rows = rows.values(*[vars[g].name for g in grouping_variables]).annotate(**annotate_args)
  #rows = rows.values(*[vars[g]['name'] for g in grouping_variables]).annotate(**annotate_args)
  #rows = rows.values(*units).annotate(**annotate_args)
  
  # Order
  rows = rows.order_by(*order_by_fields)
  #rows = rows.order_by(order_by)

  # Get total count
  count_total = rows.count()

  # Apply offset and limit
  rows = rows[offset : offset + limit]

  aaData = []
  for row in rows:
    aaData.append([vars[col].extract(row) for col in columns if vars[col].name in row])
    #aaData.append([row_extract(row, vars[col]) for col in columns if vars[col]['name'] in row])
    #aaData.append([row_extract(row, var) for var in vars if var_name(var) in row])

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
  
  return render_to_response('home.html', context_instance=RequestContext(request))

def about(request):
  
  return render_to_response('about.html', context_instance=RequestContext(request))

def results(request):
  
  result_form = ResultForm()
  return render_to_response(
    'results.html', 
    {'skip_fluid' : True, 'form' : result_form}, 
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
