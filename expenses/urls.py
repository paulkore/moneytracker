from django.conf.urls import patterns,url, include

from expenses import views

urlpatterns = patterns('',
    # TODO: this doesn't work (fails to load internal module 'conf')
    # url(r'^', include('favicon.urls')),

    url(r'^(?P<event_name_slug>[-\w]+)/$', views.EventExpensesView.as_view(), name='event-expenses'),
    url(r'^(?P<event_name_slug>[-\w]+)/expense/add/$', views.expense_form_view, name='event-expense-create'),
    url(r'^(?P<event_name_slug>[-\w]+)/expense/(?P<expense_id>\d+)/$', views.expense_form_view, name='event-expense-edit'),

    url(r'^person/add/$', views.PersonCreateView.as_view(), name='person-create'),
    url(r'^person/(?P<pk>\d+)/$', views.PersonDetailView.as_view(), name='person-detail'),
    url(r'^person/(?P<pk>\d+)/update/$', views.PersonUpdateView.as_view(), name='person-update'),
    url(r'^person/(?P<pk>\d+)/delete/$', views.PersonDeleteView.as_view(), name='person-delete'),

    url(r'^action/success/$', views.ActionSuccessView.as_view(), name='action-success'),
    url(r'^action/failure/$', views.ActionFailureView.as_view(), name='action-failure'),
)
