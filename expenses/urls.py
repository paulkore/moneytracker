from django.conf.urls import patterns,url

from expenses import views

urlpatterns = patterns('',
    url(r'^(?P<event_name_slug>[-\w]+)/$', views.EventExpensesView.as_view(), name='event-expenses'),
    url(r'^(?P<event_name_slug>[-\w]+)/expense/add/$', views.expense_form_view, name='event-expense-create'),
    url(r'^(?P<event_name_slug>[-\w]+)/expense/(?P<expense_id>\d+)/$', views.expense_form_view, name='event-expense-edit'),
    url(r'^(?P<event_name_slug>[-\w]+)/expense/(?P<expense_id>\d+)/delete/$', views.expense_delete_view, name='event-expense-delete'),

    url(r'^person/add/$', views.PersonCreateView.as_view(), name='person-create'),
    url(r'^person/(?P<pk>\d+)/$', views.PersonDetailView.as_view(), name='person-detail'),
    url(r'^person/(?P<pk>\d+)/update/$', views.PersonUpdateView.as_view(), name='person-update'),
    url(r'^person/(?P<pk>\d+)/delete/$', views.PersonDeleteView.as_view(), name='person-delete'),


    # url(r'expense/create$', views.ExpenseCreateView.as_view(), name='expense-create'),
    # url(r'expense/(?P<pk>\d+)$', views.ExpenseDetailView.as_view(), name='expense-detail'),
    # url(r'expense/(?P<pk>\d+)/update$', views.ExpenseUpdateView.as_view(), name='expense-update'),
    # url(r'expense/(?P<pk>\d+)/delete$', views.ExpenseDeleteView.as_view(), name='expense-delete'),

    url(r'^action/success/$', views.ActionSuccessView.as_view(), name='action-success'),
    url(r'^action/failure/$', views.ActionFailureView.as_view(), name='action-failure'),
)
