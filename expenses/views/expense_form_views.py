from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from expenses.forms import ExpenseForm
from expenses.models import Event, Expense


def expense_form_view(request, event_name_slug, expense_id = None):
    event = Event.find_by_name_slug(event_name_slug)
    assert event

    if expense_id is None:
        # if we are creating a new expense
        existing_expense = None
    else:
        # if we are editing an existing expense
        existing_expense = Expense.objects.get(id = expense_id)
        assert existing_expense

    if request.method == 'GET':
        # a GET request indicates that we're either
        #   - starting to create a new expense
        #   - starting to edit an existing expense

        # we'll create a blank form first, which will suffice for creating a new expense
        form = ExpenseForm(event)
        if existing_expense:
            # ...and populate it with the existing expense values, if applicable
            form.populate_from_object(existing_expense)

    elif request.method == 'POST':
        # a POST request indicates that a form was submitted and we need to process it, to either:
        #   - create a new expense with the passed data
        #   - update an existing expense with the passed data

        # create a form instance and populate it with data from the request:
        form = ExpenseForm(event, request.POST)
        if existing_expense:
            # indicate the existing expense, if applicable (this will toggle create/update behavior)
            form.expense = existing_expense

        if 'form-submit-save' in request.POST:
            # SAVE:
            if form.is_valid():
                # if form is valid, process the save and redirect to event expenses view
                form.process_save()
                return HttpResponseRedirect(reverse('expenses:event-expenses', kwargs={'event_name_slug': event_name_slug}))
            else:
                # if form is invalid, re-render the form (validation errors will be displayed)
                pass

        elif 'form-submit-delete' in request.POST:
            # DELETE:
            assert existing_expense
            existing_expense.deep_delete()
            return HttpResponseRedirect(reverse('expenses:event-expenses', kwargs={'event_name_slug': event_name_slug}))

        elif 'form-submit-cancel' in request.POST:
            # CANCEL: return to the event expenses view
            return HttpResponseRedirect(reverse('expenses:event-expenses', kwargs={'event_name_slug': event_name_slug}))

        else:
            raise Exception('Did not receive expected submit input name in POST data')

    else:
        raise Exception('HTTP method not allowed: ' + request.method)

    return render(request, 'expenses/expense_form.html',
                  {
                      'form': form,
                      'existing_expense': existing_expense,
                  })

def expense_delete_view(request, event_name_slug, expense_id):
    event = Event.find_by_name_slug(event_name_slug)
    assert event
    expense = Expense.objects.get(pk=expense_id)
    assert expense
    assert expense.event_id is event.id

    # TODO: determine whether the deep_delete() method is really necessary, rather than just delete()
    expense.deep_delete()
    #expense.delete()

    return HttpResponseRedirect(reverse('expenses:event-expenses', kwargs={'event_name_slug': event_name_slug}))

