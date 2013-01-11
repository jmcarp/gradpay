from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

from django.contrib.auth import views as auth_views
from regform import CustomAuthenticationForm, CustomRegistrationForm
from django.contrib.auth.forms import AuthenticationForm

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'gradpay.views.home', name='home'),
    url(r'^about/', 'gradpay.views.about', name='about'),
    url(r'^survey/', 'gradpay.views.survey', name='survey'),
    url(r'^results/', 'gradpay.views.results', name='results'),
    url(
      r'^accounts/register/$', 'registration.views.register',
      {
        'form_class': CustomRegistrationForm,
        'backend': 'registration.backends.default.DefaultBackend'
      },
      name='registration_register'
    ),
    url(
      r'^accounts/login/$',
      'django.contrib.auth.views.login',
      {
        'template_name' : 'registration/login.html',
        'authentication_form' : CustomAuthenticationForm,
      },
      name='auth_login'
    ),
    url(r'^accounts/', include('registration.backends.default.urls')),
    url(r'^admin/', include(admin.site.urls)),
    (r'^selectable/', include('selectable.urls')),
)
