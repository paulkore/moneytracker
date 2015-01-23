from django.conf.urls import patterns, url

from expenses import views

urlpatterns = patterns(
    '',

    # TODO: this doesn't work (fails to load internal module 'conf')
    # url(r'^', include('favicon.urls')),

    url(r'^(?P<event_name_slug>[-\w]+)/$', views.EventRecordsView.as_view(), name='event-records'),
    url(r'^(?P<event_name_slug>[-\w]+)/record/add/$', views.expense_form_view, name='event-record-create'),
    url(r'^(?P<event_name_slug>[-\w]+)/record/(?P<record_id>\d+)/$', views.expense_form_view, name='event-record-edit'),

    url(r'^person/add/$', views.PersonCreateView.as_view(), name='person-create'),
    url(r'^person/(?P<pk>\d+)/$', views.PersonDetailView.as_view(), name='person-detail'),
    url(r'^person/(?P<pk>\d+)/update/$', views.PersonUpdateView.as_view(), name='person-update'),
    url(r'^person/(?P<pk>\d+)/delete/$', views.PersonDeleteView.as_view(), name='person-delete'),

)
