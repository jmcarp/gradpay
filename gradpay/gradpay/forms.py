# Imports
import datetime
import hashlib
import random
import re

# Django imports
from django import forms
from django.forms import fields
from django.forms import ModelForm
from django.forms.widgets import SelectMultiple, RadioSelect
from django.utils.translation import ugettext as _

# Project imports
from models import Department, Institution, Support, Survey
from lookups import DepartmentLookup, InstitutionLookup
from widgets import HelpSelectMultiple
from widgets import FKAutoCompleteWidget

from django.template.loader import render_to_string
from django.contrib.sites.models import Site
from django.core.mail import send_mail
import settings

# Selectable imports
from selectable.forms import AutoCompleteWidget

# Crispy imports
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, HTML, Div, Field, Fieldset, ButtonHolder, Button, Submit

remove_message = unicode(_('Hold down "Control", or "Command" on a Mac, to select more than one.'))

GROUPING_CHOICES = (
  ('institution', 'Institution'), 
  ('state', 'State'), 
  ('department', 'Department')
)

DISPLAY_CHOICES = (
  ('avg_stipend', 'Stipend'), 
  ('avg_teach_frac', 'Teaching %')
)

class ResultForm(forms.Form):
  
  grouping_variables = forms.MultipleChoiceField(required=False, choices=GROUPING_CHOICES, initial=[choice[0] for choice in GROUPING_CHOICES], widget=forms.CheckboxSelectMultiple)
  display_variables = forms.MultipleChoiceField(required=False, choices=DISPLAY_CHOICES, initial=[choice[0] for choice in DISPLAY_CHOICES], widget=forms.CheckboxSelectMultiple)

  def __init__(self, *args, **kwargs):

    self.helper = FormHelper()
    self.helper.layout = Layout(
      Div(
        Div(
          Div(
            Div(
              Div('grouping_variables', css_class='span3'),
              Div('display_variables', css_class='span3'),
              css_class='row-fluid'
            ),
            Div(
              id='table-request-alert',
              css_class='row-fluid'
            ),
            Div(
              Button('#', 'Get Results', onclick='make_table()', css_class='btn btn-primary'),
              css_class='row-fluid'
            ),
            HTML('<hr>')
          ),
          css_class='offset1 span10'
        ),
        css_class='row-fluid'
      )
    )

    super(ResultForm, self).__init__(*args, **kwargs)

class SurveyForm(ModelForm):
  
  institution = forms.CharField(max_length=256, widget=FKAutoCompleteWidget(InstitutionLookup))
  department = forms.CharField(max_length=256, label='Field of study', help_text='Choose the best available option. Be as specific as possible.', widget=FKAutoCompleteWidget(DepartmentLookup))

  def __init__(self, *args, **kwargs):
    
    self.helper = FormHelper()

    self.helper.form_class = 'form-horizontal'
    self.helper.add_input(Submit('submit', 'Submit'))

    # Set up fieldsets
    self.helper.layout = Layout(
      HTML("""
        <div class="alert alert-block alert-info">
          Please choose the best answer for each question.
        </div>
      """),
      Div(
        Fieldset(
          'Program details',
          'email', 'institution', 'department', 'degree', 'international_student', 'start_year', 'graduation_year',
        ),
        id='details', css_class='anchor'
      ),
      Div(
        Fieldset(
          'Stipend and support: Current academic year',
          HTML("""
            <div class="alert alert-info">
              If you are a current student, please answer for the <strong>current</strong> year only.
              <br />
              If you have already graduated, please answer for the <strong>last</strong> year of your program.
            </div>
          """),
          'stipend', 'support_types', 'summer_stipend', 'tuition_coverage', 'fees',
          id='stipend-now'
        ),
        id='stipend-current', css_class='anchor'
      ),
      Div(
        Fieldset(
          'Stipend and support: General',
          'total_terms', 'teaching_terms', 'contract', 'part_time_work', 
          'student_loans', 'union_member',
          id='stipend-general'
        ),
        id='stipend-general', css_class='anchor'
      ),
      Div(
        Fieldset(
          'Health benefits',
          'health_benefits', 'dental_benefits', 'vision_benefits', 'leave',
        ),
        id='benefits', css_class='anchor'
      ),
      Div(
        Fieldset(
          'General comments',
          'satisfaction', 'comments',
        ),
        id='comments', css_class='anchor'
      )
    )

    # Widen form fields
    self.helper.filter(basestring, max_level=2).wrap(Field, css_class='span5')

    super(SurveyForm, self).__init__(*args, **kwargs)

    for name, field in self.fields.items():

      # Remove default help_text
      # Based on http://djangosnippets.org/snippets/2400/
      if field.help_text:
        field.help_text = field.help_text.replace(remove_message, '').strip()

      # Add HTML5 attribs
      if field.required != False:
        field.widget.attrs['required'] = 'required'
      if isinstance(field, fields.IntegerField):
        field.widget.input_type = 'number'
      if isinstance(field.widget, SelectMultiple):
        field.widget.attrs['size'] = len(field.choices)
      if hasattr(field, 'min_value') and field.min_value is not None:
        field.widget.attrs['min'] = field.min_value
      if hasattr(field, 'max_value') and field.max_value is not None:
        field.widget.attrs['max'] = field.max_value

  class Meta:
    model = Survey
    widgets = {
      'support_types' : HelpSelectMultiple(
        help_texts=[val[0] for val in Support.objects.values_list('tooltip')]
      ),
      'satisfaction' : RadioSelect(attrs={'class':'radio'}),
    }

  def clean(self):
    
    # Get cleaned data
    cleaned_data = super(ModelForm, self).clean()
    
    # Stop year must be later than start year
    start_year = cleaned_data.get('start_year')
    stop_year = cleaned_data.get('stop_year')

    if start_year and stop_year:
      if start_year > stop_year:
        msg = 'Stop year must be greater than or equal to start year.'
        self._errors['stop_year'] = self.error_class([msg])
    
    # Teaching terms must be <= total terms
    total_terms = cleaned_data.get('total_terms')
    teaching_terms = cleaned_data.get('teaching_terms')
    research_terms = cleaned_data.get('research_terms')

    if teaching_terms and total_terms:
      if teaching_terms > total_terms:
        self._errors['teaching_terms'] = self.error_class(['Teaching terms must be less than or equal to total terms'])
    if research_terms and total_terms:
      if teaching_terms > total_terms:
        self._errors['research_terms'] = self.error_class(['Research terms must be less than or equal to total terms'])

    # Return cleaned data
    return cleaned_data
  
  def clean_email(self):
    
    # Email must end in .edu
    if not re.search('\.edu$', self.cleaned_data['email'], re.I):
      raise forms.ValidationError(_('Must be a valid academic [.edu] email address.'))

    return self.cleaned_data['email']

  def clean_institution(self):
    
    # Institution must be in suggestions
    institution = self.cleaned_data.get('institution')
    if institution:
      try:
        institution_record = Institution.objects.get(name=institution)
      except:
        raise forms.ValidationError(_('Institution must be chosen from suggestions.'))
    
    return institution_record

  def clean_department(self):
    
    # Department must be in suggestions
    department = self.cleaned_data.get('department')
    if department:
      try:
        department_record = Department.objects.get(name=department)
      except:
        raise forms.ValidationError(_('Department must be chosen from suggestions.'))
    
    return department_record

  def save(self):
    
    instance = super(SurveyForm, self).save(commit=False)
    
    # Generate random salt
    salt = hashlib.sha1(str(random.random())).hexdigest()[:5]

    # Generate activation key
    instance.activation_key = hashlib.sha1(salt + instance.email).hexdigest()

    # Set active to False
    instance.active = False
    
    instance.save()

    # Email user
    mail_context = {
      'activation_key' : instance.activation_key,
      'site' : Site.objects.get_current(),
    }

    subject = render_to_string('activation_email_subject.txt', mail_context)
    subject = ''.join(subject.splitlines())
    message = render_to_string('activation_email.txt', mail_context)
    
    # Send email
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [instance.email])
