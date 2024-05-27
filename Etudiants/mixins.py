from django.contrib.auth import get_user_model
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone

MAX_FAILED_ATTEMPTS = 5
LOCKOUT_TIME = timezone.timedelta(minutes=30)  # Durée de blocage (30 minutes dans cet exemple)

class LoginAttemptsMixin:
    def post(self, request, *args, **kwargs):
        form = self.get_form()
        identifiant = form.data.get('username')
        password = form.data.get('password')
        
        if identifiant and password:
            User = get_user_model()
            try:
                user = User.objects.get(identifiant=identifiant)  
                if not user.is_active and user.account_locked_until:
                    if user.check_password(password):
                        if timezone.now() > user.account_locked_until + LOCKOUT_TIME:
                            # Réactiver l'utilisateur si les informations sont correctes
                            user.is_active = True
                            user.failed_login = 0
                            user.account_locked_until = None
                            user.save()
                        else:
                            messages.error(self.request, "Votre compte est bloqué en raison de trop nombreuses tentatives de connexion infructueuses. Veuillez contacter l'administrateur.")
                            return redirect(reverse('login_etudiant'))  
                    else:
                        return self.form_invalid(form)
            except User.DoesNotExist:
                pass

        return super().post(request, *args, **kwargs)
    
    
    def form_invalid(self, form):
        identifiant = form.data.get('username')
        if identifiant:
            User = get_user_model()
            try:
                user = User.objects.get(identifiant=identifiant)
                user.failed_login += 1
                user.save()
                if user.failed_login >= MAX_FAILED_ATTEMPTS:
                    user.account_locked_until = timezone.now()
                    user.is_active = False
                    user.save()
                    messages.error(self.request, "Votre compte est bloqué en raison de trop nombreuses tentatives de connexion infructueuses. Veuillez contacter l'administrateur.")
                    return redirect(reverse('login_etudiant'))
            except User.DoesNotExist:
                pass
        messages.error(self.request, "Nom d'utilisateur ou mot de passe incorrect.")
        return super().form_invalid(form)
    

    def form_valid(self, form):
        user = form.get_user()
        user.failed_login = 0
        user.account_locked_until = None
        user.save()
        return super().form_valid(form)