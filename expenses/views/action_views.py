from django.template import Context
from django.views import generic


class ActionSuccessView(generic.TemplateView):
    template_name = "expenses/action.html"

    def get_context_data(self, **kwargs):
        context = Context({
            'success': True,
        })

        return context

class ActionFailureView(generic.TemplateView):
    template_name = "expenses/action.html"

    def get_context_data(self, **kwargs):
        context = Context({
            'success': False,
        })

        return context