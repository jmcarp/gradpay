# Imports
import datetime

# Django imports
from django.forms import fields
from django.forms import ModelForm
from django.forms.widgets import RadioSelect, RadioFieldRenderer
from form_utils.forms import BetterModelForm
from selectable.forms import AutoCompleteWidget
from django.utils.translation import ugettext as _
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe

# Project imports
from models import Survey
from lookups import DisciplineLookup, InstitutionLookup

remove_message = unicode(_('Hold down "Control", or "Command" on a Mac, to select more than one.'))

class MyRadioRenderer(RadioFieldRenderer):
  def render(self):
    return mark_safe(u'\n%s\n' % u'\n'.join([u'%s'
                % force_unicode(w) for w in self]))

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Fieldset, ButtonHolder, Submit

class SurveyForm(ModelForm):
  
  def __init__(self, *args, **kwargs):
    
    self.helper = FormHelper()
    self.helper.form_class = 'form-horizontal'
    self.helper.add_input(Submit('submit', 'Submit'))

    # Set up fieldsets
    self.helper.layout = Layout(
      Fieldset(
        'Please describe your training program',
        'institution', 'department', 'area', 'degree', 'start_year', 'stop_year'
      ),
      Fieldset(
        'Please describe your stipend or salary', 
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
    #self.helper.filter(PrependedAppendedText, max_level=1).wrap(Field, css_class='span6')
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
      'satisfaction' : RadioSelect(attrs={'class':'radio'}, renderer=MyRadioRenderer),
    }

  def clean(self):
    
    cleaned_data = super(ModelForm, self).clean()

    start_year = cleaned_data.get('start_year')
    stop_year = cleaned_data.get('stop_year')

    if start_year and stop_year:
      if start_year > stop_year:
        msg = 'Stop year must be greater than or equal to start year.'
        self._errors['stop_year'] = self.error_class([msg])

    return cleaned_data

class old_SurveyForm(BetterModelForm):
  
  start_year = fields.IntegerField(min_value=1900, max_value=datetime.datetime.now().year+10)
  stop_year = fields.IntegerField(min_value=1900, max_value=datetime.datetime.now().year+10)

  def __init__(self, *args, **kwargs):
    
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
      if hasattr(field, 'min_value') and field.min_value is not None:
        field.widget.attrs['min'] = field.min_value
      if hasattr(field, 'max_value') and field.max_value is not None:
        field.widget.attrs['max'] = field.max_value

  class Meta:
    model = Survey
    widgets = {
      'department' : AutoCompleteWidget(DisciplineLookup),
      'institution' : AutoCompleteWidget(InstitutionLookup),
      'satisfaction' : RadioSelect(attrs={'class':'radio'}, renderer=MyRadioRenderer),
    }
    fieldsets = [
                  ('Please describe your training program', {'fields' : ['institution', 'department', 'area', 'degree', 'start_year', 'stop_year'] }),
                  ('Please describe your stipend or salary', {'fields' : ['salary', 'salary_unit', 'salary_types', 'summer_funding', 'tuition', 'contract'] }),
                  ('Please describe your health benefits', {'fields' : ['health_benefits', 'dental_benefits', 'vision_benefits'] }),
                  ('Please enter any additional comments', {'fields' : ['satisfaction', 'comments'] }),
                ]

  def clean(self):
    
    cleaned_data = super(BetterModelForm, self).clean()

    start_year = cleaned_data.get('start_year')
    stop_year = cleaned_data.get('stop_year')

    if start_year and stop_year:
      if start_year > stop_year:
        msg = 'Stop year must be greater than or equal to start year.'
        self._errors['stop_year'] = self.error_class([msg])

    return cleaned_data
