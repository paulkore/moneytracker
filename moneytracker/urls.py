from django.conf.urls import patterns, url, include
from django.contrib import admin
from django.views.generic import TemplateView

from moneytracker import views

urlpatterns = patterns(
    '',

    url(r'^admin/', include(admin.site.urls)),

    url(r'^$', views.login_redirect_view),
    url(r'^login/$', views.login_view, name='login'),
    url(r'^logout/$', views.logout_view, name='logout'),
    url(r'^landing/$', views.landing_view, name='landing'),

    url(r'^account/$', views.account_view, name='account'),
    url(r'^account/event-make-default/(?P<participant_id>\d+)$',
        views.account_event_make_default,
        name='account-event-make-default'),

    url(r'^(?P<event_name_slug>[-\w]+)/$', views.event_records_view, name='event-records'),

    url(r'^(?P<event_name_slug>[-\w]+)/record/create-expense/$', views.money_record_view, name='create-expense'),
    url(r'^(?P<event_name_slug>[-\w]+)/record/create-transfer/$', views.money_record_view, name='create-transfer'),
    url(r'^(?P<event_name_slug>[-\w]+)/record/(?P<record_id>\d+)/$', views.money_record_view, name='edit-record'),


)





