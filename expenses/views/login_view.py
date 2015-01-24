from django.contrib.auth import authenticate, login, logout
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render

from expenses.forms import LoginForm
from expenses.models import Event


def _landing_page_redirect(user):
    # TODO: the landing page should be the following:
    # - the user's account page (default, as this page always exists)
    # - one of the user's events' pages (configurable from the account page)

    # for now, the landing page is the first event that's relevant:
    events = Event.find_by_user(user)
    assert len(events) > 0, 'Currently supporting only users with at least 1 event'
    return HttpResponseRedirect(reverse('expenses:event-records', kwargs={'event_name_slug': events[0].name_slug}))


def login_view(request):

    if request.user.is_authenticated():
        # if a user is already logged in, redirect somewhere else!
        return _landing_page_redirect(request.user)

    if request.method == 'GET':
        # a GET request indicates that someone navigated to this page
        # create a blank form, and render it
        form = LoginForm()

    elif request.method == 'POST':
        # a POST request indicates that a form was submitted and we need to process the login attempt

        # create a form instance and populate it with data from the request:
        form = LoginForm(request.POST)

        if form.is_valid():
            # if form input is valid, attempt authenticating the user
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is None:
                form = LoginForm()
                form.error_message = 'Invalid username / password combination'
            else:
                # if authentication succeeded, check whether the account is active / inactive
                if not user.is_active:
                    form = LoginForm()
                    form.error_message = "Account '{0}' is disabled".format(username)
                else:
                    # if account is active, login the user and redirect to the user's landing page
                    login(request, user)
                    return _landing_page_redirect(user)

        else:
            # if form input is invalid, re-render the form (validation errors will be displayed)
            pass

    else:
        raise Exception('HTTP method not allowed: ' + request.method)

    return render(request, 'expenses/login_form.html', {'form': form})


def logout_view(request):
    logout(request)
    return render(request, 'expenses/login_form.html', {'form': LoginForm()})


