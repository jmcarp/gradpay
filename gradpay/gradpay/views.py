# 
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required

# Import models
from models import Survey
from forms import SurveyForm

import json
from django.http import HttpResponse
from django.db.models import Avg, Count
from django.db.models import Q

relation_map = {
  'institution' : 'name',
  'department' : 'name',
}

stored_vars = [
  'institution__name',
  'institution__state',
  'department__name',
]
computed_vars = [
  'avg_salary',
  'num_resp',
]
vars = stored_vars + computed_vars

sort_map = {
  'asc' : '',
  'dsc' : '-',
}

def results_json(request):
  
  # Get sEcho [datatables security param]
  sEcho = request.GET.get('sEcho', 0)

  units = request.GET.get('units', 'institution')
  units = units.split(',')
  for unitidx in range(len(units)):
    unit = units[unitidx]
    if unit in relation_map:
      units[unitidx] += '__' + relation_map[unit]
  if 'institution__name' in units:
    units.append('institution__state')
  
  like = request.GET.get('sSearch', '')
  like_lookup = ''
  if like:
    like_lookup = Q(**{stored_vars[0] + '__icontains' : like})
    for var in stored_vars[1:]:
      like_lookup = like_lookup | Q(**{var + '__icontains' : like})

  order = request.GET.get('order', 'institution__name')
  sort_col = request.GET.get('iSortCol_0', '0')
  try:
    sort_col = int(sort_col)
  except:
    sort_col = 0
  sort_var = vars[sort_col]
  sort_dir = request.GET.get('sSortDir_0', 'dsc')
  try:
    sort_sign = sort_map[sort_dir]
  except:
    sort_sign = '-'
  direc = request.GET.get('direc', '-')
  order_by = sort_sign + sort_var

  offset = request.GET.get('iDisplayStart', 0)
  offset = max(0, int(offset))
  limit = request.GET.get('iDisplayLength', 10)
  limit = min(int(limit), 100)
  
  rows = Survey.objects

  # Filter by search term
  if like_lookup:
    rows = rows.filter(like_lookup)

  # Compute average salary
  rows = rows.values(*units).annotate(avg_salary=Avg('salary'), num_resp=Count('salary'))
  
  # Order
  rows = rows.order_by(order_by)

  # Get total count
  count_total = rows.count()

  # Apply offset and limit
  rows = rows[offset : offset + limit]

  aaData = []
  for row in rows:
    aaData.append([row[var] for var in vars if var in row])

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

def home(request):
  
  return render_to_response('home.html', context_instance=RequestContext(request))

def about(request):
  
  return render_to_response('about.html', context_instance=RequestContext(request))

def results(request):
  
  return render_to_response('comingsoon.html', {'skip_fluid' : True}, context_instance=RequestContext(request))

def contact(request):

  return render_to_response('contact.html', context_instance=RequestContext(request))

@login_required
def survey(request):
  
  # Check for previously saved survey
  try:
    survey = Survey.objects.filter(user=request.user).get()
  except:
    survey = None

  # Save data or display form
  if request.method == 'POST':
    survey_form = SurveyForm(request.POST, instance=survey)
    if survey_form.is_valid():
      # Add user info to survey
      survey_form.instance.user = request.user
      # Save data
      survey_form.save()
      # Redirect
      return render_to_response('survey_complete.html', context_instance=RequestContext(request))
  else:
    survey_form = SurveyForm(instance=survey)

  # Display form
  return render_to_response('survey.html', {'form' : survey_form}, RequestContext(request))
