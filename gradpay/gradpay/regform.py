"""
Custom form for user creation.
"""

# Imports
import re

# Django imports
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import ugettext_lazy as _

# Registration imports
from registration.forms import RegistrationForm

# Crispy imports
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.forms.widgets import PasswordInput, TextInput

class CustomAuthenticationForm(AuthenticationForm):
  
  #username = forms.CharField(widget=TextInput(attrs={'class': 'span2','placeholder': 'Email'}))
  #password = forms.CharField(widget=PasswordInput(attrs={'class': 'span2','placeholder':'Password'}))

  def __init__(self, *args, **kwargs):
    
    self.helper = FormHelper()
    self.helper.form_class = 'form-horizontal'
    self.helper.add_input(Submit('submit', 'Submit'))
  
    super(CustomAuthenticationForm, self).__init__(*args, **kwargs)

class CustomRegistrationForm(RegistrationForm):
  
  def __init__(self, *args, **kwargs):
    
    self.helper = FormHelper()
    self.helper.form_method = 'post'
    self.helper.form_class = 'form-horizontal'
    self.helper.add_input(Submit('submit', 'Submit'))

    super(RegistrationForm, self).__init__(*args, **kwargs)

  def clean_email(self):
    
    # Email must be unique
    # Modified from registration.forms.RegistrationFormUniqueEmail
    if User.objects.filter(email__iexact=self.cleaned_data['email']):
      raise forms.ValidationError(_('This email address is already in use.'))

    # Email must end in .edu
    if not re.search('\.edu$', self.cleaned_data['email'], re.I):
      raise forms.ValidationError(_('Must be a valid academic [.edu] email address.'))

    # Email is OK
    return self.cleaned_data['email']
