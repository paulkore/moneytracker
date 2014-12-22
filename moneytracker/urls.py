from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',

    url(r'^admin/', include(admin.site.urls)),

    url(r'^polls/', include('polls.urls', namespace='polls')),

    url(r'^moneytracker/', include('expenses.urls', namespace='expenses')),


)
