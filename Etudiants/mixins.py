from django.contrib.auth import get_user_model
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from django.core.cache import cache


MAX_FAILED_ATTEMPTS = 3
LOCKOUT_TIME = timezone.timedelta(minutes=1)  # Durée de blocage (30 minutes)




class CombinedLoginBlockMixin:
    
    """Mixin pour bloquer l'utilisateur et le couple (adresse IP, session) si le nombre de tentatives infructueuses est trop important"""
    
    def post(self, request, *args, **kwargs):
        form = self.get_form()
        identifiant = form.data.get('username')
        password = form.data.get('password')
        client_ip = self.request.META.get('REMOTE_ADDR')
        session_key = request.session.session_key or request.session.create()

        if identifiant and password:
            User = get_user_model()
            try:
                user = User.objects.get(identifiant=identifiant)
                
                # Vérifier si le compte est bloqué
                if not user.is_active and user.account_locked_until:
                    if user.check_password(password):
                        if timezone.now() > user.account_locked_until + LOCKOUT_TIME:
                            # Réactiver l'utilisateur si les informations sont correctes
                            user.is_active = True
                            user.failed_login = 0
                            user.account_locked_until = None
                            self.clear_failed_attempts(client_ip, session_key)
                            # print(self.is_ip_session_blocked(client_ip, session_key))
                            # print(cache.get(f'failed_attempts_{client_ip}_{session_key}'))
                            user.save()
                        else:
                            # print(self.is_ip_session_blocked(client_ip, session_key))
                            # print(cache.get(f'failed_attempts_{client_ip}_{session_key}'))
                            messages.error(self.request, "Votre compte ou connexion a été temporairement suspendu en raison d'un nombre excessif de tentatives de connexion infructueuses. Veuillez contacter l'administrateur.")
                            return redirect(reverse('login_etudiant'))
                    else:
                        return self.form_invalid(form)

            except User.DoesNotExist:
                pass

        return super().post(request, *args, **kwargs)

    def form_invalid(self, form):
        identifiant = form.data.get('username')
        client_ip = self.request.META.get('REMOTE_ADDR')
        session_key = self.request.session.session_key or self.request.session.create()

        if identifiant:
            User = get_user_model()
            try:
                user = User.objects.get(identifiant=identifiant)
                user.failed_login += 1
                # Obtenir le nombre de tentatives de connexion infructueuses pour cette adresse IP et cette session
                failed_attempts = self.get_failed_attempts(client_ip, session_key)
                failed_attempts += 1
                # Mettre à jour le nombre de tentatives infructueuses
                self.set_failed_attempts(client_ip, session_key, failed_attempts)
                
                user.save()

                # Vérifier le nombre de tentatives infructueuses de l'utilisateur
                if user.failed_login >= MAX_FAILED_ATTEMPTS :
                    user.account_locked_until = timezone.now()
                    user.is_active = False
                    # Bloquer l'adresse IP et la session
                    self.block_ip_session(client_ip, session_key)
                    user.save()
                    messages.error(self.request, "Votre compte ou connexion a été temporairement suspendu en raison d'un nombre excessif de tentatives de connexion infructueuses. Veuillez contacter l'administrateur.")
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
        client_ip = self.request.META.get('REMOTE_ADDR')
        session_key = self.request.session.session_key
        self.clear_failed_attempts(client_ip, session_key)
        return super().form_valid(form)

    def get_failed_attempts(self, client_ip, session_key):
        # Obtenir le nombre de tentatives infructueuses pour cette adresse IP et cette session
        return cache.get(f'failed_attempts_{client_ip}_{session_key}', 0)

    def set_failed_attempts(self, client_ip, session_key, failed_attempts):
        # Mettre à jour le nombre de tentatives infructueuses
        cache.set(f'failed_attempts_{client_ip}_{session_key}', failed_attempts, LOCKOUT_TIME.total_seconds())

    def clear_failed_attempts(self, client_ip, session_key):
        # Effacer le nombre de tentatives infructueuses
        cache.delete(f'failed_attempts_{client_ip}_{session_key}')

    def block_ip_session(self, client_ip, session_key):
        # Bloquer l'adresse IP et la session
        cache.set(f'blocked_ip_session_{client_ip}_{session_key}', True, LOCKOUT_TIME.total_seconds())

    def is_ip_session_blocked(self, client_ip, session_key):
        # Vérifier si l'adresse IP et la session sont bloquées
        return cache.get(f'blocked_ip_session_{client_ip}_{session_key}', False)
