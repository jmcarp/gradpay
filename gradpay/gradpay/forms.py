# Imports
import datetime

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

# Selectable imports
from selectable.forms import AutoCompleteWidget

# Crispy imports
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, HTML, Field, Fieldset, ButtonHolder, Submit

remove_message = unicode(_('Hold down "Control", or "Command" on a Mac, to select more than one.'))

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
      Fieldset(
        'Program details',
        'institution', 'department', 'degree', 'international_student', 'start_year', 'graduation_year'
      ),
      Fieldset(
        'Stipend and support: Current academic year',
        HTML("""
          <div class="alert alert-info">
            If you are a current student, please answer for the <strong>current</strong> year only.
            <br />
            If you have already graduated, please answer for the <strong>last</strong> year of your program.
          </div>
        """),
        'stipend', 'support_types', 'summer_stipend', 'tuition_coverage'
      ),
      Fieldset(
        'Stipend and support: General',
        'total_terms', 'teaching_terms', 'research_terms', 'contract', 'student_loans'
      ),
      Fieldset(
        'Health benefits',
        'health_benefits', 'dental_benefits', 'vision_benefits'
      ),
      Fieldset(
        'General comments',
        'satisfaction', 'comments'
      )
    )

    # Widen form fields
    self.helper.filter(basestring, max_level=1).wrap(Field, css_class='span6')

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

  def clean_institution(self):
    
    # Institution must be in suggestions
    institution = self.cleaned_data.get('institution')
    if institution:
      try:
        institution_record = Institution.objects.get(name=institution)
      except:
        raise forms.ValidationError(_('Institution must be chosen from suggestions.'))
    
    return institution_record
    return self.cleaned_data['institution']

  def clean_department(self):
    
    # Department must be in suggestions
    department = self.cleaned_data.get('department')
    if department:
      try:
        department_record = Department.objects.get(name=department)
      except:
        raise forms.ValidationError(_('Department must be chosen from suggestions.'))
    
    return department_record
    return self.cleaned_data['department']
