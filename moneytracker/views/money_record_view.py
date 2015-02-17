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
        # A new record is being created
        existing_record = None
    else:
        # An existing record is being edited
        existing_record = MoneyRecord.objects.get(id=record_id)
        if not existing_record:
            raise Http404()

    if request.method == 'GET':
        # a GET request indicates that we're either
        #   - starting to create a new record
        #   - starting to edit an existing record

        if existing_record:
            # Existing record:
            # Create a form and populate it with the existing record's values
            form = MoneyRecordForm(event)
            form.populate_from_record(existing_record)
        else:
            # New record:
            # Create a form and set the requested record type (expense or transfer)
            form = MoneyRecordForm(event)
            if 'create-expense' in request.path:
                form.set_record_type('expense')
            elif 'create-transfer' in request.path:
                form.set_record_type('transfer')
            else:
                raise Exception('Unable to detect the record type from URL')

    elif request.method == 'POST':
        # a POST request indicates that a form was submitted and we need to process it, to either:
        #   - create a new record with the passed data
        #   - update an existing record with the passed data
        #   - delete an existing record
        #   - cancel the operation

        # create a form instance and populate it with data from the request:
        form = MoneyRecordForm(event, request.POST)

        if 'form-submit-save' in request.POST:
            # SAVE:
            if form.is_valid():
                # if form is valid, save and redirect to event records view
                if existing_record:
                    form.update_existing(existing_record)
                else:
                    form.save_as_new_record()

                return HttpResponseRedirect(reverse('event-records', kwargs={'event_name_slug': event_name_slug}))
            else:
                # if form is invalid, do nothing here;
                # the form will be re-rendered, and validation errors will be displayed
                pass

        elif 'form-submit-delete' in request.POST:
            # DELETE:
            if existing_record:
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



