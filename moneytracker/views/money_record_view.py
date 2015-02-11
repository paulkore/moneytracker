from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render

from moneytracker.auth import has_event_access
from moneytracker.forms import MoneyRecordForm
from moneytracker.models import Event, MoneyRecord


def money_record_view(request, event_name_slug, record_id=None):
    user = request.user
    if not user.is_authenticated():
        return HttpResponseRedirect(reverse('login'))

    event = Event.find_by_name_slug(event_name_slug)
    if not event:
        raise Http404()
    if not has_event_access(user, event):
        raise PermissionDenied()

    if record_id is None:
        # if we are creating a new record
        existing_record = None
    else:
        # if we are editing an existing record
        existing_record = MoneyRecord.objects.get(id=record_id)
        assert existing_record

    if request.method == 'GET':
        # a GET request indicates that we're either
        #   - starting to create a new record
        #   - starting to edit an existing record

        # we'll create a blank form first, which will suffice for creating a new record
        form = MoneyRecordForm(event)
        if existing_record:
            # ...and populate it with the existing values, if applicable
            form.populate_from_object(existing_record)

    elif request.method == 'POST':
        # a POST request indicates that a form was submitted and we need to process it, to either:
        #   - create a new record with the passed data
        #   - update an existing record with the passed data

        # create a form instance and populate it with data from the request:
        form = MoneyRecordForm(event, request.POST)
        if existing_record:
            # indicate the existing record, if applicable (this will toggle create/update behavior)
            form.money_record = existing_record

        if 'form-submit-save' in request.POST:
            # SAVE:
            if form.is_valid():
                # if form is valid, process the save and redirect to event records view
                form.process()
                return HttpResponseRedirect(reverse('event-records', kwargs={'event_name_slug': event_name_slug}))
            else:
                # if form is invalid, re-render the form (validation errors will be displayed)
                pass

        elif 'form-submit-delete' in request.POST:
            # DELETE:
            assert existing_record
            existing_record.delete()
            return HttpResponseRedirect(reverse('event-records', kwargs={'event_name_slug': event_name_slug}))

        elif 'form-submit-cancel' in request.POST:
            # CANCEL: return to the event records view
            return HttpResponseRedirect(reverse('event-records', kwargs={'event_name_slug': event_name_slug}))

        else:
            raise Exception('Did not receive expected submit input name in POST data')

    else:
        raise Exception('HTTP method not allowed: ' + request.method)

    return render(request, 'money_record_form.html',
                  {
                      'form': form,
                      'existing_record': existing_record,
                  })



