from django.shortcuts import render
from django.conf import settings
from applications.projects.models import Project, Program, Type
from applications.home.models import Contact
from applications.projects.views import ProjectsListView
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from django.urls import reverse_lazy

from django.views.generic import View, TemplateView, CreateView
from django.http import  HttpResponseServerError


# forms
from .forms import ContactForm
from .functions import send_email

class HomePageView(ProjectsListView):
    template_name = 'home/index.html'
    model = Project
    cache_key = 'project_search_cache'
    


class ContactCreateView(CreateView):
    template_name = 'home/contact.html'
    form_class = ContactForm
    model = Contact
    success_url = reverse_lazy('home_app:contact_success')

    def form_valid(self, form):
        # Guardar el formulario y obtener la instancia del modelo
        self.object = form.save()

        # Obtener datos del formulario
        client_name = form.cleaned_data['full_name']
        organization = form.cleaned_data['organization']
        contact_reason = form.cleaned_data['contact_reason']
        message = form.cleaned_data['message']
        client_email = form.cleaned_data['email']

        # Correos destinatarios como admin
        admin_email = settings.ADMIN_EMAIL
        noreplay_email = settings.NOREPLY_EMAIL

        # Enviar el correo electrónico con los datos del formulario
        send_email(
            # Subject
            'Razón de contacto: ' + contact_reason + ' - Banco de Proyectos',
            # Content
            'Ha recibido el siguiente comentario: \n' +
            'Nombre de usuario: ' + client_name + '\n' +
            'Organización: ' + organization + '\n' +
            'Razón de contacto: ' + contact_reason + '\n' +
            'Mensaje: \n\n' + message,
            # From email
            noreplay_email[0],
            # To emails
            admin_email
        )

        # Enviar copia al cliente del correo electrónico con los datos del formulario
        send_email(
            # Subject
            'Razón de contacto: ' + contact_reason + ' - Banco de Proyectos',
            # Content
            'Su comentario ha sido recepcionado correctamente. A continuación se adjunta una copia de su comentario: \n\n'
            + form.cleaned_data['message'],
            # From email
            noreplay_email[0],
            # To emails
            [client_email]
        )

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['programs'] = Program.objects.all()
        context['types'] = Type.objects.all()

        return context

class ContactSuccess(TemplateView):
    template_name = 'home/contact-success.html'

class Error404(TemplateView):
    template_name = 'home/404.html'
    
class Error500(TemplateView):
    template_name = "home/500.html"

    @classmethod
    def as_error_view(cls):

        v = cls.as_view()
        def view(request):
            r = v(request)
            r.render()
            return r
        return view
    
class Error503(TemplateView):
    template_name = 'home/503.html'

    @classmethod
    def as_error_view(cls):
        v = cls.as_view()

        def view(request):
            r = v(request)
            r.render()
            return r

        return view

    
