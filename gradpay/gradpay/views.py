# 
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required

# Import models
from models import Survey
from forms import SurveyForm

def home(request):
  
  return render_to_response('home.html', context_instance=RequestContext(request))

def about(request):
  
  return render_to_response('about.html', context_instance=RequestContext(request))

def results(request):
  
  return render_to_response('comingsoon.html', context_instance=RequestContext(request))

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
      return render_to_response('survey_complete.html')
  else:
    survey_form = SurveyForm(instance=survey)

  # Display form
  return render_to_response('survey.html', {'form' : survey_form}, RequestContext(request))
