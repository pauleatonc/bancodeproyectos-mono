from django.shortcuts import render
from django.core.mail import send_mail
from django.urls import reverse_lazy, reverse
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponseRedirect
from django.contrib import messages

from django.views.generic import (
    View,
    CreateView,
    TemplateView
)

from django.views.generic.edit import (
    FormView
)

from .forms import UserRegisterForm, LoginForm, UpdatePasswordForm, VerificationSignInForm, PasswordRecoveryForm

# Models
from .models import User
from applications.projects.models import Program, Type

from .functions import code_generator, validar_rut


class UserRegisterView(LoginRequiredMixin, UserPassesTestMixin, FormView):
    template_name = 'users/register.html'
    form_class = UserRegisterForm
    model = User
    success_url = reverse_lazy('users_app:register_success')

    def test_func(self):
        return self.request.user.is_staff

    def handle_no_permission(self):
        messages.error(self.request, 'Para acceder al panel de administrador necesitas ingresar con usuario autorizado')
        return redirect('users_app:user-login')

    def form_valid(self, form):
        # Genera un código para validar a través de correo
        #codigo = code_generator()

        usuario = User.objects.create_user(
            rut=form.cleaned_data['rut'],
            password=form.cleaned_data['password1'],
            nombres=form.cleaned_data['nombres'],
            primer_apellido=form.cleaned_data['primer_apellido'],
            segundo_apellido=form.cleaned_data['segundo_apellido'],
            email=form.cleaned_data['email'],

            #codregistro = codigo
        )

        return super(UserRegisterView, self).form_valid(form)

        """# enviar el codigo al email del user
        asunto = 'Email de confirmación ArchiPartner'
        mensaje = 'El código de verificación es: ' + codigo
        email_remitente = 'jhearquitecto@gmail.com'
        #
        send_mail(asunto, mensaje, email_remitente, [form.cleaned_data['email'],])

        # Redirigir a pantalla de validación
        return HttpResponseRedirect(
            reverse(
                'users_app:user-verification',
                kwargs={'pk': usuario.id}
            )
        )"""

class LoginUser(FormView):
    template_name = 'users/login.html'
    form_class = LoginForm

    def form_valid(self, form):
        user = authenticate(
            rut=form.cleaned_data['rut'],
            password=form.cleaned_data['password']
        )
        login(self.request, user)

        # Agregamos un método para redirigir a la página desde donde se originó el login
        # en el html se debe agregar ?next={{ request.path }} a continuación del href {% url 'users_app:user-login' %}
        # para recoger el id del proyecto visitado
        next_url = self.request.GET.get('next', None)
        if next_url:
            return redirect(next_url)
        else:
            return redirect('projects_app:project-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['programs'] = Program.objects.all()
        context['types'] = Type.objects.all()

        return context


class LogoutView(View):

    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect(self.request.META.get('HTTP_REFERER', '/'))


class UpdatePasswordView(LoginRequiredMixin, FormView):
    template_name = 'users/update.html'
    form_class = UpdatePasswordForm
    success_url = reverse_lazy('users_app:user-login')
    login_url = reverse_lazy('users_app:user-login')

    def form_valid(self, form):
        usuario = self.request.user
        user = authenticate(
            email=usuario.email,
            password=form.cleaned_data['password1']
        )

        if user:
            new_password = form.cleaned_data['password2']
            usuario.set_password(new_password)
            usuario.save()

        logout(self.request)
        return super(UpdatePasswordView, self).form_valid(form)

class CodeVerificationView(FormView):
    template_name = 'users/verification.html'
    form_class = VerificationSignInForm
    success_url = reverse_lazy('users_app:user-login')

    def get_form_kwargs(self):
        kwargs = super(CodeVerificationView, self).get_form_kwargs()
        kwargs.update({
            'pk': self.kwargs['pk'],
        })
        return kwargs

    def form_valid(self, form):
        #
        User.objects.filter(
            id=self.kwargs['pk']
        ).update(
            is_active=True
        )
        return super(CodeVerificationView, self).form_valid(form)

class AdminHomeView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'users/admin_home.html'
    login_url = reverse_lazy('users_app:user-login')

    def test_func(self):
        return self.request.user.is_staff

    def handle_no_permission(self):
        messages.error(self.request, 'Para acceder al panel de administrador necesitas ingresar con usuario autorizado')
        return redirect('users_app:user-login')

class RegisterSuccess(LoginRequiredMixin, TemplateView):
    template_name = 'users/register_success.html'
    login_url = reverse_lazy('users_app:user-login')

    def test_func(self):
        return self.request.user.is_staff

    def handle_no_permission(self):
        messages.error(self.request, 'No tienes los permisos para crear usuarios')
        return redirect('users_app:user-login')

class PasswordRecoveryMain(TemplateView):
    def get(self, request):
        form = PasswordRecoveryForm()
        return render(request, 'users/password_recovery_main.html', {'form': form})

    def post(self, request):
        form = PasswordRecoveryForm(request.POST)

        if form.is_valid():
            rut = form.cleaned_data['rut']
            user = User.objects.get(rut=rut)

            if user.tipo_usuario == 'SUBDERE':
                # Realiza las acciones correspondientes para el tipo de usuario 'SUBDERE'
                return redirect('subdere_link')
            elif user.tipo_usuario == 'BANCO':
                # Realiza las acciones correspondientes para el tipo de usuario 'BANCO'
                return redirect('banco_link')

        return render(request, 'users/password_recovery_main.html', {'form': form})