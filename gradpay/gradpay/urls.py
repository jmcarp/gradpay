from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

from django.contrib.auth import views as auth_views
from django.contrib.auth.forms import AuthenticationForm

import settings

urlpatterns = patterns('',
    url(r'^$', 'gradpay.views.home', name='home'),
    url(r'^about/$', 'gradpay.views.about', name='about'),
    url(r'^faq/$', 'gradpay.views.faq', name='faq'),
    url(r'^hist/$', 'gradpay.views.hist', name='hist'),
    url(r'^get_stipends/$', 'gradpay.views.get_stipends', name='get_stipends'),
    url(r'^survey/$', 'gradpay.views.survey', name='survey'),
    url(r'^activate/(\w+)/$', 'gradpay.views.activate', name='activate'),
    url(r'^results/$', 'gradpay.views.results', name='results'),
    url(r'^results_json', 'gradpay.views.results_json', name='results_json'),
    url(r'^contact/$', 'gradpay.views.contact', name='contact'),
    url(r'^channel.html$', 'gradpay.views.channel', name='channel'),
    url(r'^admin/', include(admin.site.urls)),
    (r'^selectable/', include('selectable.urls')),
    (r'^static/(.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
)
