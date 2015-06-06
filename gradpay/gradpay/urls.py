from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

import settings

from views import InstitutionEndpoint, DepartmentEndpoint

urlpatterns = patterns('',
    url(r'^$', 'gradpay.views.home', name='home'),
    url(r'^about/$', 'gradpay.views.about', name='about'),
    url(r'^linkedinfo/$', 'gradpay.views.linkedinfo', name='linkedinfo'),
    url(r'^get_stipends/$', 'gradpay.views.get_stipends', name='get_stipends'),
    url(r'^survey/$', 'gradpay.views.survey', name='survey'),
    url(r'^activate/(\w+)/$', 'gradpay.views.activate', name='activate'),
    url(r'^results/$', 'gradpay.views.results_table', name='table'),
    url(r'^results/table/$', 'gradpay.views.results_table', name='table'),
    url(r'^results/figure/$', 'gradpay.views.results_figure', name='figure'),
    url(r'^results_json', 'gradpay.views.results_json', name='results_json'),
    url(r'^results/map/$', 'gradpay.views.results_choro', name='results_choro'),
    url(r'^results/scatter/$', 'gradpay.views.results_scatter', name='results_scatter'),
    url(r'^api/institution/', InstitutionEndpoint.as_view()),
    url(r'^api/department/', DepartmentEndpoint.as_view()),
    url(r'^choro_json', 'gradpay.views.choro_json', name='choro_json'),
    url(r'^scatter_json', 'gradpay.views.scatter_json', name='scatter_json'),
    url(r'^contact/$', 'gradpay.views.contact', name='contact'),
    url(r'^privacy/$', 'gradpay.views.privacy', name='privacy'),
    url(r'^channel.html$', 'gradpay.views.channel', name='channel'),
    url(r'^admin/', include(admin.site.urls)),
    (r'^selectable/', include('selectable.urls')),
    (r'^static/(.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
)

#    url(r'^results/$', 'gradpay.views.results', name='results'),
#    url(r'^hist/$', 'gradpay.views.hist', name='hist'),
#    url(r'^faq/$', 'gradpay.views.faq', name='faq'),
