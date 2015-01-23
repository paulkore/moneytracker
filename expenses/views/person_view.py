from django.core.urlresolvers import reverse, reverse_lazy
from django.views import generic
''' from expenses.models import Person'''

# TODO: re-purpose this for user account creation / profile editing

'''
class PersonDetailView(generic.DetailView):
    template_name = "expenses/person_detail.html"
    model = Person
    fields = '__all__'

class PersonCreateView(generic.CreateView):
    template_name = "expenses/person_form.html"
    model = Person
    fields = '__all__'
    def get_success_url(self):
        return reverse('expenses:person-detail', kwargs={'pk': self.object.pk})

class PersonUpdateView(generic.UpdateView):
    template_name = "expenses/person_form.html"
    model = Person
    fields = '__all__'
    def get_success_url(self):
        return reverse('expenses:person-detail', kwargs={'pk': self.object.pk})

class PersonDeleteView(generic.DeleteView):
    model = Person
    success_url = reverse_lazy('expenses:person-list')
'''