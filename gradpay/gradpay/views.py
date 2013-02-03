# 
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required

# Import models
from models import Survey
from forms import ResultForm, SurveyForm

import json
from django.http import HttpResponse
from django.db.models import Avg, Count
from django.db.models import Q

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

def row_extract(row, var):
  if isinstance(var, tuple):
    return var[1](row[var[0]])
  return row[var]

def var_name(var):
  if isinstance(var, tuple):
    return var[0]
  return var

stored_vars = [
  'institution__name',
  'institution__state',
  'department__name',
]
computed_vars = [
  'avg_stipend',
  ('avg_teach_frac', fmt_factory(True, 0)),
  'num_resp',
]
vars = stored_vars + computed_vars

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
  units = request.GET.get('units', 'institution')
  units = units.split(',')
  units = [relation_map[unit] for unit in units if unit in relation_map]
  
  # Get display variables
  display_variables = request.GET.get('display', 'salary')
  display_variables = display_variables.split(',')
  if not display_variables[0]:
    display_variables = [] 
  display_variables.append('num_resp')
  annotate_args = {}
  for dv in display_variables:
    annotate_args[dv] = annotate_map[dv]

  # Get search term
  like = request.GET.get('sSearch', '')
  like_lookup = ''
  if like:
    like_lookup = Q(**{stored_vars[0] + '__icontains' : like})
    for var in stored_vars[1:]:
      like_lookup = like_lookup | Q(**{var + '__icontains' : like})

  sort_col = request.GET.get('iSortCol_0', '0')
  sort_col = int(sort_col)
  sort_var = vars[sort_col]

  # Get sort direction
  sort_dir = request.GET.get('sSortDir_0', 'dsc')
  sort_sign = sort_map[sort_dir]
  order_by = sort_sign + sort_var

  # Get offset and limit
  offset = request.GET.get('iDisplayStart', 0)
  offset = max(0, int(offset))
  limit = request.GET.get('iDisplayLength', 10)
  limit = min(int(limit), 100)
  
  rows = Survey.objects

  # Filter by search term
  if like_lookup:
    rows = rows.filter(like_lookup)

  # Compute average stipend
  rows = rows.values(*units).annotate(**annotate_args)
  #rows = rows.values(*units).annotate(
  #  avg_stipend=Avg('stipend'), 
  #  avg_teach_frac=Avg('_teaching_fraction'), 
  #  num_resp=Count('stipend')
  #)
  
  # Order
  rows = rows.order_by(order_by)

  # Get total count
  count_total = rows.count()

  # Apply offset and limit
  rows = rows[offset : offset + limit]

  aaData = []
  for row in rows:
    aaData.append([row_extract(row, var) for var in vars if var_name(var) in row])
    #aaData.append([row[var] for var in vars if var in row])

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
  return render_to_response('results.html', {'skip_fluid' : True, 'form' : result_form}, context_instance=RequestContext(request))

def contact(request):

  return render_to_response('contact.html', context_instance=RequestContext(request))

#@login_required
def survey(request):
  
  ## Check for previously saved survey
  #try:
  #  survey = Survey.objects.filter(user=request.user).get()
  #except:
  #  survey = None

  # Save data or display form
  if request.method == 'POST':
    survey_form = SurveyForm(request.POST)
    #survey_form = SurveyForm(request.POST, instance=survey)
    if survey_form.is_valid():
      ## Add user info to survey
      #survey_form.instance.user = request.user
      # Save data
      survey_form.save()
      # Redirect
      return render_to_response('survey_complete.html', context_instance=RequestContext(request))
  else:
    survey_form = SurveyForm(instance=survey)

  # Display form
  return render_to_response('survey.html', {'form' : survey_form}, RequestContext(request))
