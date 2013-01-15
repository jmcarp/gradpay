# Imports
import datetime

# Django imports
from django.forms import fields
from django.forms import ModelForm
from django.forms.widgets import RadioSelect
from django.forms.widgets import SelectMultiple
from django.utils.translation import ugettext as _

# Project imports
from models import Discipline, Institution, Support, Survey
from lookups import DisciplineLookup, InstitutionLookup
from widgets import HelpSelectMultiple

# Selectable imports
from selectable.forms import AutoCompleteWidget

# Crispy imports
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, HTML, Field, Fieldset, ButtonHolder, Submit

remove_message = unicode(_('Hold down "Control", or "Command" on a Mac, to select more than one.'))

class SurveyForm(ModelForm):
  
  def __init__(self, *args, **kwargs):
    
    self.helper = FormHelper()

    self.helper.form_class = 'form-horizontal'
    self.helper.add_input(Submit('submit', 'Submit'))

    # Set up fieldsets
    self.helper.layout = Layout(
      HTML("""
        <div class="alert alert-block alert-info">
          <h4>Note:</h4>
          Please choose the best answer for each question.
        </div>
      """),
      Fieldset(
        'Please describe your training program',
        'institution', 'department', 'area', 'degree', 'start_year', 'stop_year'
      ),
      Fieldset(
        'Please describe your stipend or salary', 
        HTML("""
          <div class="alert alert-info">
            If your support varies from year to year, please answer for the <strong>current</strong> year.
          </div>
        """),
        'salary', 'salary_unit', 'salary_types', 'summer_funding', 'tuition', 'contract', 'student_loans'
      ),
      Fieldset(
        'Please describe your health benefits', 
        'health_benefits', 'dental_benefits', 'vision_benefits'
      ),
      Fieldset(
        'Please enter any additional comments', 
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

  class Meta:
    model = Survey
    widgets = {
      'department' : AutoCompleteWidget(DisciplineLookup),
      'institution' : AutoCompleteWidget(InstitutionLookup),
      'salary_types' : HelpSelectMultiple(
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

    # Institution must be in suggestions
    institution = cleaned_data.get('institution')
    if institution:
      try:
        institution_record = Institution.objects.get(name=institution)
      except:
        msg = 'Institution must be chosen from suggestions.'
        self._errors['institution'] = self.error_class([msg])
    
    # Department must be in suggestions
    department = cleaned_data.get('department')
    if department:
      try:
        department_record = Discipline.objects.get(name=department)
      except:
        msg = 'Department must be chosen from suggestions.'
        self._errors['department'] = self.error_class([msg])

    return cleaned_data

#class old_SurveyForm(BetterModelForm):
#  
#  start_year = fields.IntegerField(min_value=1900, max_value=datetime.datetime.now().year+10)
#  stop_year = fields.IntegerField(min_value=1900, max_value=datetime.datetime.now().year+10)
#
#  def __init__(self, *args, **kwargs):
#    
#    super(SurveyForm, self).__init__(*args, **kwargs)
#    
#    for name, field in self.fields.items():
#      
#      # Remove default help_text
#      # Based on http://djangosnippets.org/snippets/2400/
#      if field.help_text:
#        field.help_text = field.help_text.replace(remove_message, '').strip()
#
#      # Add HTML5 attribs
#      if field.required != False:
#        field.widget.attrs['required'] = 'required'
#      if isinstance(field, fields.IntegerField):
#        field.widget.input_type = 'number'
#      if hasattr(field, 'min_value') and field.min_value is not None:
#        field.widget.attrs['min'] = field.min_value
#      if hasattr(field, 'max_value') and field.max_value is not None:
#        field.widget.attrs['max'] = field.max_value
#
#  class Meta:
#    model = Survey
#    widgets = {
#      'department' : AutoCompleteWidget(DisciplineLookup),
#      'institution' : AutoCompleteWidget(InstitutionLookup),
#    }
#    #  'satisfaction' : RadioSelect(attrs={'class':'radio'}, renderer=MyRadioRenderer),
#    fieldsets = [
#                  ('Please describe your training program', {'fields' : ['institution', 'department', 'area', 'degree', 'start_year', 'stop_year'] }),
#                  ('Please describe your stipend or salary', {'fields' : ['salary', 'salary_unit', 'salary_types', 'summer_funding', 'tuition', 'contract'] }),
#                  ('Please describe your health benefits', {'fields' : ['health_benefits', 'dental_benefits', 'vision_benefits'] }),
#                  ('Please enter any additional comments', {'fields' : ['satisfaction', 'comments'] }),
#                ]
#
#  def clean(self):
#    
#    cleaned_data = super(BetterModelForm, self).clean()
#
#    start_year = cleaned_data.get('start_year')
#    stop_year = cleaned_data.get('stop_year')
#
#    if start_year and stop_year:
#      if start_year > stop_year:
#        msg = 'Stop year must be greater than or equal to start year.'
#        self._errors['stop_year'] = self.error_class([msg])
#
#    return cleaned_data
