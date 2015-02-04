from django.conf.urls import patterns, url

from expenses import views

urlpatterns = patterns(
    '',

    url(r'^$', views.login_redirect_view),
    url(r'^login/$', views.login_view, name='login'),
    url(r'^logout/$', views.logout_view, name='logout'),

    url(r'^(?P<event_name_slug>[-\w]+)/$', views.event_records_view, name='event-records'),
    url(r'^(?P<event_name_slug>[-\w]+)/record/add/$', views.money_record_view, name='money-record-create'),
    url(r'^(?P<event_name_slug>[-\w]+)/record/(?P<record_id>\d+)/$', views.money_record_view, name='money-record-edit')
)





