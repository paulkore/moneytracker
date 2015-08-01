from django.contrib.auth import authenticate, login, logout
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render

from trakr.account import landing_page_redirect
from trakr.forms import LoginForm


def login_view(request):

    if request.user.is_authenticated():
        # if a user is already logged in, redirect somewhere else!
        return landing_page_redirect(request.user)

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
                form.custom_error = 'Invalid username / password combination'
            else:
                # if authentication succeeded, check whether the account is active / inactive
                if not user.is_active:
                    form = LoginForm()
                    form.custom_error = "Account '{0}' is disabled".format(username)
                else:
                    # if account is active, login the user and redirect to the user's landing page
                    login(request, user)
                    return landing_page_redirect(user)

        else:
            # if form input is invalid, re-render the form (validation errors will be displayed)
            pass

    else:
        raise Exception('HTTP method not allowed: ' + request.method)

    return render(request, 'login.html', {'form': form})


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('login'))


def login_redirect_view(request):
    return HttpResponseRedirect(reverse('login'))


def landing_view(request):
    if request.user.is_authenticated():
        return landing_page_redirect(request.user)
    else:
        return HttpResponseRedirect(reverse('login'))
