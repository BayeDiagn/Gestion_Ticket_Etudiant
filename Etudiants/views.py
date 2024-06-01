import datetime
from django.utils import timezone
from django.urls import reverse, reverse_lazy
from django.shortcuts import redirect, render,get_object_or_404


from Admin.models import User
from Etudiants.forms import EtudiantCreationForm, SendTicketForm
from Etudiants.models import Etudiant, Transaction

from rest_framework.views import APIView
from Etudiants.serializers import EtudiantSerializer
from Etudiants.utils import PayTech
from Gestion_Tickets import settings
from Personnels.serializers import PersonnelSerializer, TicketConsommerSerializer
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet,ReadOnlyModelViewSet
from rest_framework.decorators import action
from rest_framework import status
from django.contrib.auth.views import LoginView,PasswordChangeView,PasswordResetCompleteView,PasswordResetView,PasswordResetDoneView
from django.views.generic import DetailView,CreateView
from django.contrib.auth.decorators import login_required,user_passes_test
from django.contrib.auth import  logout, update_session_auth_hash, get_user_model


from Personnels.models import Personnel, TicketConsommer
from Tickets.models import Ticket_Dej, Ticket_Repas
from django.db import transaction
from django.db.models import Q , Sum, Max
from django.contrib import messages
from notifications.models import Notification
from notifications.signals import notify
from django.http import JsonResponse
from django.shortcuts import HttpResponse

import paydunya
from paydunya import InvoiceItem, Store,Invoice

from Gestion_Tickets.settings import PAYDUNYA_ACCESS_TOKENS, SESSION_EXPIRE_AFTER_INACTIVITY,api_key,api_secret
import uuid
from .mixins import CombinedLoginBlockMixin
from django.contrib.auth.mixins import LoginRequiredMixin










# Activer le mode 'test'. Le debug est à False par défaut
# paydunya.debug = True

# Configurer les clés d'API
# paydunya.api_keys = PAYDUNYA_ACCESS_TOKENS

# Configuration des informations de votre service/entreprise
# store = Store(name='Uadb Gestion_Ticket')









#decorateur controlant l'acces a la page accueil
def etudiant_required(view_func):
    decorated_view_func = user_passes_test(
        lambda user: (user.is_authenticated and user.is_etudiant) or (user.is_authenticated and user.is_boutiquier),
        login_url='login_etudiant'
    )(view_func)
    return decorated_view_func



#Accueil
@etudiant_required
@login_required
def etudiant_home(request):
    request.session.set_expiry(SESSION_EXPIRE_AFTER_INACTIVITY)  # Après 30 minutes d'inactivité, la session de l'utilisateur expirera, et il devra se reconnecter.
    update_session_auth_hash(request, request.user)  # Mettre à jour le hachage d'authentification de session
    
    etudiant = Etudiant.objects.get(id=request.user.id)
    
    tickets_dej_etudiant = Ticket_Dej.objects.filter(etudiant=etudiant)
    nbre_tickets_dej = int(sum(ticket.nbre_tickets_dej for ticket in tickets_dej_etudiant))
    
    tickets_repas_etudiant = Ticket_Repas.objects.filter(etudiant=etudiant)
    nbre_tickets_repas = int(sum(ticket.nbre_tickets_repas for ticket in tickets_repas_etudiant))
    
    notifications = Notification.objects.filter(recipient=request.user, unread=True)
    nbre = notifications.count()
   
    #print(str(uuid.uuid4()))
    
    #paiement avec paytech
    if request.method == 'POST':
        petits_dej = request.POST.get('pdej')
        dejeuners = request.POST.get('dej')
        
        item_name = 'ticket'
        
        if not petits_dej:
            petits_dej = '0'
            item_name='ticket repas'
        if not dejeuners:
            dejeuners = '0'
            item_name='ticket petit dej'
        
        
        try:
            petits_dej =int(petits_dej)
            dejeuners = int(dejeuners)
        except ValueError:
            # Gérer le cas où les valeurs ne sont pas des nombres valides
            petits_dej = int('0')
            dejeuners = int('0')
            
        request.session['petits_dej'] = petits_dej
        request.session['dejeuners'] = dejeuners
            
        item_price = (petits_dej*50) + (dejeuners*100)
        
        if item_price == 50 or item_price == 100 :
            item_price = item_price + (100 - item_price)
        
        
        # Instanciation de la classe PayTech
        pay_tech = PayTech(api_key, api_secret)
        
        # Configuration des paramètres de la requête de paiement
        pay_tech.setQuery({
            'item_name': item_name,
            'item_price': item_price,
            'command_name': f"Paiement {item_name} etudiant via PayTech"
        })
        pay_tech.setTestMode(True)
        pay_tech.setCurrency('XOF')
        pay_tech.setRefCommand(str(uuid.uuid4()))
        pay_tech.setNotificationUrl({
            'ipn_url': 'https://192.168.1.49:8000/ipn',
            'success_url': 'https://192.168.1.49:8000/payment-done/',
            'cancel_url': 'https://192.168.1.49:8000/accueil/',
        })
        pay_tech.setMobile(False)
        
        # Envoi de la requête de paiement
        response = pay_tech.send()

        if response['success'] == 1:
            redirect_url = response['redirect_url']
            return redirect(redirect_url)
        else:
            error_message = ', '.join(response['errors'])
            # print(error_message)
            # messages.error(request, error_message)
            # form.add_error(None, error_message)
        
     
    currentTransactions = Transaction.objects.filter(Q(etudiant=request.user.id) & (Q(description__icontains='Achat') | Q(description__icontains='Envoi'))).order_by('-id')
    currentTransactions = currentTransactions[0:3]
    
    
    context = {"nbre_tickets_dej":nbre_tickets_dej,"nbre_tickets_repas":nbre_tickets_repas,
               "notifications":notifications,"nbre":nbre,'currentTransactions':currentTransactions }
    return render(request,'Etudiants/etudiant_home.html',context)


#Redirection apres succes du paiement
@etudiant_required
@login_required
def payment_done(request):
    petits_dej = request.session.get('petits_dej')
    dejeuners = request.session.get('dejeuners')
    etudiant = Etudiant.objects.get(identifiant=request.user.identifiant)
    
    if petits_dej is None and dejeuners is None:
        # Aucun ticket à créer
        del request.session['petits_dej']
        del request.session['dejeuners']
        return redirect('home_etudiant')

    if dejeuners == 0 or dejeuners is None:
        if petits_dej is not None:
            pdej = Ticket_Dej(nbre_tickets_dej=petits_dej, etudiant=etudiant)
            pdej.save()
            notify.send(request.user, recipient=request.user, verb=f'Vous avez acheté {petits_dej} ticket(s) de petit-déj')
            transaction = Transaction(description=f"Achat de {petits_dej} ticket(s) Petit-déj.", tickets_pdej=petits_dej, etudiant=etudiant)
            transaction.save()

    elif petits_dej == 0 or petits_dej is None:
        if dejeuners is not None:
            dej = Ticket_Repas(nbre_tickets_repas=dejeuners, etudiant=etudiant)
            dej.save()
            notify.send(request.user, recipient=request.user, verb=f'Vous avez acheté {dejeuners} ticket(s) déjeuner')
            transaction = Transaction(description=f"Achat de {dejeuners} ticket(s) Déjeuner.", tickets_dej=dejeuners, etudiant=etudiant)
            transaction.save()

    else:
        if petits_dej is not None and dejeuners is not None:
            pdej = Ticket_Dej(nbre_tickets_dej=petits_dej, etudiant=etudiant)
            pdej.save()
            dej = Ticket_Repas(nbre_tickets_repas=dejeuners, etudiant=etudiant)
            dej.save()
            notify.send(request.user, recipient=request.user, verb=f'Vous avez acheté {dejeuners} ticket(s) déjeuner', description=f'Et {petits_dej} ticket(s) petit-déjeuner')
            transaction = Transaction(description=f"Achat de {petits_dej} ticket(s) Petit-déj et {dejeuners} ticket(s) Déjeuner.", tickets_pdej=petits_dej, tickets_dej=dejeuners, etudiant=etudiant)
            transaction.save()

    del request.session['petits_dej']
    del request.session['dejeuners']

    return redirect('home_etudiant')
    
      
  
#Annulation du paiement   
@etudiant_required
@login_required
def payment_canceled(request):
    return redirect('home_etudiant')




#Supprimer les notifications
@etudiant_required
@login_required
def clear_notification(request):
    Notification.objects.filter(recipient=request.user).delete()
    return redirect('home_etudiant')




#login
class EtudiantLoginView(CombinedLoginBlockMixin, LoginView):
    template_name = "Etudiants/etudiant_login.html"
    
 
    
    def get_success_url(self):
        #user = get_user_model()
        user = self.request.user
        if user.is_etudiant or user.is_boutiquier:
            return reverse_lazy('home_etudiant')
        else:
            return reverse_lazy('personnel-home')




# class EtudiantCreateView(CreateView):
#     model = Etudiant
#     form_class = EtudiantCreationForm
#     #fields = ['first_name','last_name','identifiant','email','password1','password2']
#     template_name = 'Etudiants/etudiant_inscription.html'
#     success_url = reverse_lazy('login_etudiant')




#view de deconnexion
def etudiant_deconnected(request):
    logout(request)
    
    return redirect("login_etudiant")



#Detail_etudiant
class EtudiantDetailView(LoginRequiredMixin,DetailView):
    context_object_name = "etudiant"
    template_name = "Etudiants/etudiant_profil.html"
    model = Etudiant
    
    

 
 
    
#Changement mot de passe
class EtudiantPasswordChangeView( PasswordChangeView):
    template_name = "Etudiants/etudiant_changedPassword.html"
    success_url=reverse_lazy('password_reset_complete')



#Page vue apres changement
#@method_decorator(etudiant_required, name='dispatch')
class EtudiantPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = "Etudiants/etudiant_passwordComplet.html"
    
    


#Transaction User
@etudiant_required
@login_required
def etudiant_transaction(request):
    
    tickets_achat = Transaction.objects.filter(etudiant=request.user.id,description__icontains='Achat').order_by('-id')
    tickets_envoi = Transaction.objects.filter(etudiant=request.user.id,description__icontains='Envoi').order_by('-id')
    tickets_recept = Transaction.objects.filter(etudiant=request.user.id,description__icontains='Reception').order_by('-id')
    #tickets_conso = Transaction.objects.filter(etudiant=request.user.id,description__icontains='Consommation')
    
    
    
    context = {'tickets_achat':tickets_achat,'tickets_envoi':tickets_envoi,
               'tickets_recept':tickets_recept }
    return render(request,'Etudiants/etudiant_transaction.html',context)



class MyPasswordRestView(PasswordResetView):
    template_name='Etudiants/etudiant_resetPassword.html'
    
    

class MyPasswordResetDoneView(PasswordResetDoneView):
    template_name='Etudiants/etudiant_emailSend.html'
    
    
@etudiant_required
@login_required
@transaction.atomic
def sendTicket(request):

    form = SendTicketForm()
    if request.method == 'POST':
        form = SendTicketForm(data=request.POST)
        if form.is_valid():
            code_permenant = form.cleaned_data.get('cp')
            nbreticket = form.cleaned_data.get('nbre_tickets')
            ticket_type = form.cleaned_data.get('Typeofticket')
            
            etudiantsend = get_object_or_404(Etudiant, identifiant=request.user.identifiant)
            
            #Verifier si l'utilisateur est un boutiquier
            if etudiantsend.is_boutiquier:
                messages.error(request, "Vous n'êtes pas autorisé à effectuer cette opération!!")
                # return render(request, 'Etudiants/send_ticket.html', {'form': form}) ou
                return redirect('sendticket')
            
            try:
                etudiantreceive = Etudiant.objects.get(identifiant=code_permenant)
            except Etudiant.DoesNotExist:
                messages.error(request, 'L\'étudiant récepteur n\'existe pas')
                return redirect('sendticket')
            
             
            if ticket_type == 'dej':
                try:
                    tickets_dej_etudiant_sender = Ticket_Dej.objects.filter(etudiant=etudiantsend)
                    nbre_tickets_dej_max = max((ticket.nbre_tickets_dej for ticket in tickets_dej_etudiant_sender), default=0)
                    
                    if nbreticket <= nbre_tickets_dej_max:
                        if nbreticket >0 :
                            pdej = Ticket_Dej(nbre_tickets_dej=nbreticket, etudiant=etudiantreceive)
                            pdej.save()
                            etudiantsend.decrementer_ticket_dej(nbreticket)
                            nbreticket = int(nbreticket)
                            messages.success(request, f'{int(nbreticket)} Ticket(s) Petit-déjeuner envoyé(s) à {etudiantreceive.first_name} {etudiantreceive.last_name}.')
                            notify.send(request.user, recipient=etudiantreceive, verb=f'Vous avez reçu {nbreticket} ticket(s) de petit-déj', description=f'De la part de {etudiantsend.first_name} {etudiantsend.last_name}')
                            transactionsender = Transaction(description=f"Envoi de {nbreticket} ticket(s) Petit-déjeuner à {etudiantreceive.first_name} {etudiantreceive.last_name}.", etudiant=etudiantsend)
                            transactionsender.save()
                            transactionreceiver = Transaction(description=f"Reception de {nbreticket} ticket(s) Petit-déj offert(s) par {etudiantsend.first_name} {etudiantsend.last_name}.", etudiant=etudiantreceive)
                            transactionreceiver.save()
                            return redirect('sendticket')
                        elif nbreticket ==0 :
                            messages.error(request, 'Le nombre de tickets doit supérieur à zéro(0)!!')
                        # else :
                        #     messages.error(request, 'Nombre de tickets incorrect!!')
                    elif nbre_tickets_dej_max ==0 :
                            messages.error(request, 'Nombre de tickets Petit-Déjeuner insuffisant!!')
                    else:
                        messages.error(request, f'Vous ne pouvez pas envoyer plus de {nbre_tickets_dej_max} tickets petit-dej!!')
                except Ticket_Dej.DoesNotExist:
                    messages.error(request, 'Nombre de tickets Petit-déjeuner insuffisant!')
                return redirect('sendticket')
                
                
            if ticket_type == 'repas':
                try:
                    tickets_repas_etudiant_sender = Ticket_Repas.objects.filter(etudiant=etudiantsend)
                    nbre_tickets_repas_max = max((ticket.nbre_tickets_repas for ticket in tickets_repas_etudiant_sender), default=0)
                    
                    if nbreticket <= nbre_tickets_repas_max: 
                        if nbreticket >0 :
                            repas = Ticket_Repas(nbre_tickets_repas=nbreticket, etudiant=etudiantreceive)
                            repas.save()
                            etudiantsend.decrementer_ticket_repas(nbreticket)
                            nbreticket = int(nbreticket)
                            messages.success(request, f'{int(nbreticket)} Ticket(s) Déjeuner envoyé(s) à {etudiantreceive.first_name} {etudiantreceive.last_name}.')
                            notify.send(request.user, recipient=etudiantreceive, verb=f'Vous avez reçu {nbreticket} ticket(s) de déjeuner', description=f'De la part de {etudiantsend.first_name} {etudiantsend.last_name}')
                            transactionsender = Transaction(description=f"Envoi de {nbreticket} ticket(s) Déjeuner à {etudiantreceive.first_name} {etudiantreceive.last_name}.", etudiant=etudiantsend)
                            transactionsender.save()
                            transactionreceiver = Transaction(description=f"Reception de {nbreticket} ticket(s) Déjeuner offert(s) par {etudiantsend.first_name} {etudiantsend.last_name}.", etudiant=etudiantreceive)
                            transactionreceiver.save()
                            return redirect('sendticket')
                        elif nbreticket ==0 :
                            messages.error(request, 'Le nombre de tickets doit supérieur à zéro(0)!!')
                        # else:
                        #     messages.error(request, 'Nombre de tickets incorrect!!')
                    elif nbre_tickets_repas_max ==0 :
                            messages.error(request, 'Nombre de tickets Déjeuner insuffisant!!')
                    else:    
                        messages.error(request, f'Vous ne pouvez pas envoyer plus de {nbre_tickets_repas_max} tickets déjeuner!!')        
                except Ticket_Repas.DoesNotExist:
                    messages.error(request, 'Nombre de tickets Déjeuner insuffisant!!')
                    return redirect('sendticket')
    else:
        form = SendTicketForm()        
    

    context = {'form': form}
    return render(request, 'Etudiants/send_ticket.html', context)


#API
# class EtudiantAPIView(APIView):
    
#     def get(self,request):
#         etudiants = Etudiant.objects.all().order_by('code_permenant')
#         serializer = EtudiantSerializer(etudiants, many=True)
#         return Response(serializer.data)
    
    
    
    
#Autre façon API 
class EtudiantViewset(ReadOnlyModelViewSet):
    serializer_class = EtudiantSerializer
    #queryset = Etudiant.objects.all()
    
    def get_queryset(self):
         queryset = Etudiant.objects.all()  #annotate(nbre_tickets_repas=Count('ticket_repas')).values('id', 'code_permenant', 'first_name', 'last_name', 'nbre_tickets_repas')
         return queryset
    
    
    
    #requete vers l'api 
    @action(detail=False, methods=['get'])
    def retrieve_by_code_permanent(self, request, pk=None):
        # Récupérer l'étudiant en fonction de son code permanent
        try:
            etudiant = Etudiant.objects.get(code_qr_content=pk)
        except Etudiant.DoesNotExist:
            return Response({'error': 'Etudiant(e) non trouve'},
                    status=status.HTTP_404_NOT_FOUND)
        
        
        heure = datetime.datetime.now().hour
        
        # Vérifiez si l'étudiant est bloque
        if not etudiant.is_active:
            return Response({"error": "Compte bloque !!"}, status=status.HTTP_403_FORBIDDEN)

        #decrementer ticket dej
        if (heure)>=6 and int(heure)<=11:
            
            try:
                ticketDej =  Ticket_Dej.objects.filter(etudiant=etudiant)
                if ticketDej.exists():
                    nbre_tickets_dej_max = max(ticket.nbre_tickets_dej for ticket in ticketDej)
                    if nbre_tickets_dej_max > 0:
                        etudiant.decrementer_ticket_dej(1)
                        #transaction = Transaction(description=f"Consommation d'un ticket Petit-déjeuner.", etudiant=etudiant)
                        #transaction.save()
                        return Response({"message": "Decrementation reussie!!","typeofticket":"pdej"})
                    else:
                        return Response({"error": "Aucun ticket petit-dejeuner!!"}, status=status.HTTP_404_NOT_FOUND)
                else:
                    return Response({"error": "Aucun ticket petit-dejeuner!!"}, status=status.HTTP_404_NOT_FOUND)
            except Ticket_Dej.DoesNotExist:
                return Response({'error': 'Aucun ticket petit-dejeuner!!'},
                    status=status.HTTP_404_NOT_FOUND)
        
        
        #decrementer ticket dejeuner 
        elif (heure)>=12 and (heure)<=15 :
                try:
                    ticketRepas = Ticket_Repas.objects.filter(etudiant=etudiant)
                    if ticketRepas.exists():
                        nbre_tickets_repas_max = max(ticket.nbre_tickets_repas for ticket in ticketRepas)
                        if nbre_tickets_repas_max > 0:
                            etudiant.decrementer_ticket_repas(1)
                            # transaction = Transaction(description=f"Consommation d'un ticket diner.", etudiant=etudiant)
                            # transaction.save()
                            return Response({"message": "Decrementation reussie !!", "typeofticket": "dej"})
                        else:
                            return Response({"error": "Aucun ticket dejeuner !!"}, status=status.HTTP_404_NOT_FOUND)
                    else:
                        return Response({"error": "Aucun ticket dejeuner !!"}, status=status.HTTP_404_NOT_FOUND)
                except Ticket_Repas.DoesNotExist:
                    return Response({"error": "Aucun ticket dejeuner !!"}, status=status.HTTP_404_NOT_FOUND)
        
         #decrementer ticket dinner           
        elif (heure)>=18 and int(heure)<=23:
            try:
                ticketRepas = Ticket_Repas.objects.filter(etudiant=etudiant)
                if ticketRepas.exists():
                    nbre_tickets_repas_max = max(ticket.nbre_tickets_repas for ticket in ticketRepas)
                    if nbre_tickets_repas_max > 0:
                        etudiant.decrementer_ticket_repas(1)
                        # transaction = Transaction(description=f"Consommation d'un ticket diner.", etudiant=etudiant)
                        # transaction.save()
                        return Response({"message": "Decrementation reussie !!", "typeofticket": "dinner"})
                    else:
                        return Response({"error": "Aucun ticket dejeuner !!"}, status=status.HTTP_404_NOT_FOUND)
                else:
                    return Response({"error": "Aucun ticket dejeuner !!"}, status=status.HTTP_404_NOT_FOUND)
            except Ticket_Repas.DoesNotExist:
                return Response({"error": "Aucun ticket dejeuner !!"}, status=status.HTTP_404_NOT_FOUND)
        
        else:
            return Response({"error": "Hors delai !!"}, status=status.HTTP_404_NOT_FOUND)
              
        # Sérialiser les détails de l'étudiant
        serializer = self.get_serializer(etudiant)
        # Retourner les détails de l'étudiant dans la réponse
        return Response(serializer.data)
    
@etudiant_required
@login_required
def changeQrCode(request, pk):
    etudiant = get_object_or_404(Etudiant, pk=pk)
    
    if request.method == 'POST':
        
        # Enregistrer le nouveau QR code
        etudiant.save()
        
        messages.success(request, 'QrCode modifié avec succés')
        #print(etudiant.code_qr_content)
        return redirect('detail_etudiant', pk=pk)
        
    
    context = {'etudiant': etudiant}
    return render(request, 'Etudiants/etudiant_profil.html', context)
    
    
#TicketConsommer
class TicketConsommerViewset(APIView):
    serializer_class = TicketConsommerSerializer
    
    def get_queryset(self):
         queryset = TicketConsommer.objects.all()  
         return queryset
    
    def get(self, request, pk=None):
        try:
            personnel = Personnel.objects.get(identifiant=pk)
        except Personnel.DoesNotExist:
            return Response({'error': 'Personnel non trouvé'}, status=status.HTTP_404_NOT_FOUND)
        
        tickets = self.get_queryset().filter(personnel=personnel)
        serializer = TicketConsommerSerializer(tickets, many=True)
        return Response(serializer.data)
    
    
    def post(self, request,pk=None):
        #identifiant = request.data.get('identifiant')
        type_ticket = request.data.get('type_ticket')
        quantity = request.data.get('quantity')
        
        try:
            personnel = Personnel.objects.get(identifiant=pk)
        except Personnel.DoesNotExist:
            return Response({'error': 'Personnel non trouvé'}, status=status.HTTP_404_NOT_FOUND)
            
        today = timezone.now().date()
        
        # Vérifie si un ticket du même type a déjà été consommé aujourd'hui
        ticket_exist = TicketConsommer.objects.filter(personnel=personnel, type_ticket=type_ticket, date=today).first()
        
        if ticket_exist:
            # Si un ticket existe, mettez simplement à jour la quantité
            ticket_exist.quantity += int(quantity)
            ticket_exist.save()
            serializer = TicketConsommerSerializer(ticket_exist)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            # Si aucun ticket n'existe, créez un nouveau ticket
            ticket = TicketConsommer(type_ticket=type_ticket, quantity=quantity, personnel=personnel, date=today)
            ticket.save()
            serializer = TicketConsommerSerializer(ticket)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
               
    
    
                    
    
    

        
    

