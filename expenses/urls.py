from django.conf.urls import patterns, url

from expenses import views

urlpatterns = patterns(
    '',

    # TODO: this doesn't work (fails to load internal module 'conf')
    #
    # url(r'^', include('favicon.urls')),

    url(r'^login/$', views.login_view, name='login'),
    url(r'^logout/$', views.logout_view, name='logout'),

    url(r'^(?P<event_name_slug>[-\w]+)/$', views.EventRecordsView.as_view(), name='event-records'),
    url(r'^(?P<event_name_slug>[-\w]+)/record/add/$', views.money_record_view, name='money-record-create'),
    url(r'^(?P<event_name_slug>[-\w]+)/record/(?P<record_id>\d+)/$', views.money_record_view, name='money-record-edit')
)





