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
from crispy_forms.layout import Layout, HTML, Submit

class CustomAuthenticationForm(AuthenticationForm):
  """
  AuthenticationForm with crunchy layout
  """
  
  def __init__(self, *args, **kwargs):
    
    self.helper = FormHelper()
    self.helper.form_class = 'form-horizontal'
    self.helper.add_input(Submit('submit', 'Submit'))
  
    super(CustomAuthenticationForm, self).__init__(*args, **kwargs)

attrs_dict = {'class' : 'required'}

class CustomRegistrationForm(RegistrationForm):
  """
  RegistrationForm with crunchy layout and custom validation
  """

  username = forms.RegexField(
    regex=r'^[\w.@+-]+$',
    max_length=30,
    widget=forms.TextInput(attrs=attrs_dict),
    label=_("Username"),
    error_messages={'invalid': _("This value may contain only letters, numbers and @/./+/-/_ characters.")}
  )
  email = forms.EmailField(widget=forms.TextInput(
    attrs=dict(attrs_dict,
    maxlength=75)),
    label=_("Email address")
  )
  password1 = forms.CharField(widget=forms.PasswordInput(
    attrs=attrs_dict, render_value=False),
    label=_("Password")
  )
  password2 = forms.CharField(widget=forms.PasswordInput(
    attrs=attrs_dict, render_value=False),
    label=_("Re-enter password")
  )

  def __init__(self, *args, **kwargs):
    
    self.helper = FormHelper()
    self.helper.form_method = 'post'
    self.helper.form_class = 'form-horizontal'
    self.helper.add_input(Submit('submit', 'Submit'))

    self.helper.layout = Layout(
      HTML("""
        <div class="alert alert-info">
          Note: You must register with an academic [.edu] email address.
        </div>
      """),
      'username',
      'email',
      'password1',
      'password2'
    )

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
