import datetime
from decimal import Decimal
from django.urls import reverse_lazy
from django.shortcuts import redirect, render

from Etudiants.forms import EtudiantCreationForm, SendTicketForm
from Etudiants.models import Etudiant, Transaction

from rest_framework.views import APIView
from Etudiants.serializers import EtudiantSerializer
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework import status
from django.contrib.auth.views import LoginView,PasswordChangeView,PasswordResetCompleteView,PasswordResetView,PasswordResetDoneView
from django.views.generic import DetailView,CreateView
from django.contrib.auth.decorators import login_required,user_passes_test
from django.contrib.auth import  logout, update_session_auth_hash

from Personnels.models import Personnel
from Tickets.models import Ticket_Dej, Ticket_Repas
from django.db import transaction
from django.db.models import Q , Sum
from django.contrib import messages
from notifications.models import Notification
from notifications.signals import notify
from django.http import JsonResponse
from django.shortcuts import HttpResponse

import paydunya
from paydunya import InvoiceItem, Store,Invoice

from Gestion_Tickets.settings import PAYDUNYA_ACCESS_TOKENS, SESSION_EXPIRE_AFTER_INACTIVITY





# Activer le mode 'test'. Le debug est à False par défaut
paydunya.debug = True

# Configurer les clés d'API
paydunya.api_keys = PAYDUNYA_ACCESS_TOKENS

# Configuration des informations de votre service/entreprise
store = Store(name='Uadb Gestion_Ticket')









#decorateur controlant l'acces a la page accueil
def etudiant_required(view_func):
    decorated_view_func = user_passes_test(
        lambda user: user.is_authenticated and user.is_etudiant,
        login_url='login_etudiant'
    )(view_func)
    return decorated_view_func



#Accueil
@etudiant_required
@login_required
def etudiant_home(request):
    # request.session.set_expiry(SESSION_EXPIRE_AFTER_INACTIVITY)  # Après 30 minutes d'inactivité, la session de l'utilisateur expirera, et il devra se reconnecter.
    # update_session_auth_hash(request, request.user)  # Mettre à jour le hachage d'authentification de session
    
    etudiant = Etudiant.objects.get(id=request.user.id)
    
    tickets_dej_etudiant = Ticket_Dej.objects.filter(etudiant=etudiant)
    nbre_tickets_dej = int(sum(ticket.nbre_tickets_dej for ticket in tickets_dej_etudiant))
    
    tickets_repas_etudiant = Ticket_Repas.objects.filter(etudiant=etudiant)
    nbre_tickets_repas = int(sum(ticket.nbre_tickets_repas for ticket in tickets_repas_etudiant))
    
    notifications = Notification.objects.filter(recipient=request.user, unread=True)
    nbre = notifications.count()

    #paiement avec paydunya
    if request.method == 'POST':
        petits_dej = request.POST.get('pdej')
        dejeuners = request.POST.get('dej')
        
        
        name = 'ticket'
        prix_unit = 150

        
        if not petits_dej:
            petits_dej = '0'
            name='ticket_repas'
            prix_unit=100
        if not dejeuners:
            dejeuners = '0'
            name='ticket_petit_dej'
            prix_unit=50
        
        
        try:
            petits_dej =int(petits_dej)
            dejeuners = int(dejeuners)
        except ValueError:
            # Gérer le cas où les valeurs ne sont pas des nombres valides
            petits_dej = int('0')
            dejeuners = int('0')
            
        request.session['petits_dej'] = petits_dej
        request.session['dejeuners'] = dejeuners
            
        qunt = petits_dej + dejeuners
        prix_total = (petits_dej*50) + (dejeuners*100)
        
        if prix_total == 50 or prix_total == 100 :
            prix_total = prix_total + (200 - prix_total)
        if prix_total == 150 :
            prix_total = 200
        
        
        
        items = [
            InvoiceItem(
                name=name,
                quantity=qunt,
                unit_price=str(prix_unit),
                total_price=str(prix_total),
                description=name
         ),]
        
        invoice = paydunya.Invoice(store)
        
        # invoice.return_url = "http://192.168.1.41:8000/payment-done/"
        # invoice.cancel_url = "http://192.168.1.41:8000/payment-canceled/"
        invoice.return_url = "http://localhost:8000/payment-done/"
        invoice.cancel_url = "http://localhost:8000/payment-canceled/"
        
        invoice.add_items(items)
        
        
        successful, response = invoice.create()
        #print(response)
        if successful:
            return redirect(response.get('response_text'))
     
    currentTransactions = Transaction.objects.filter(Q(etudiant=request.user.id) & (Q(description__icontains='Achat') | Q(description__icontains='Envoi'))).order_by('-id')
    currentTransactions = currentTransactions[0:3]
    
    
    context = {"nbre_tickets_dej":nbre_tickets_dej,"nbre_tickets_repas":nbre_tickets_repas,
               "notifications":notifications,"nbre":nbre,'currentTransactions':currentTransactions }
    return render(request,'Etudiants/etudiant_home.html',context)




#Redirection apres succes du paiement
@etudiant_required
@login_required
def payment_done(request):
    token = request.GET.get('token')
    invoice = Invoice(store)
    successful, response = invoice.confirm(token)
    petits_dej = request.session.get('petits_dej')
    dejeuners = request.session.get('dejeuners')
    if successful:
        etudiant = Etudiant.objects.get(identifiant=request.user.identifiant)
        # etudiant.incrementer_ticket_dej(petits_dej)
        # etudiant.incrementer_ticket_repas(dejeuners)
        
        if dejeuners == 0 :
            pdej = Ticket_Dej(nbre_tickets_dej=petits_dej,etudiant=etudiant)
            pdej.save()
            notify.send(request.user, recipient=request.user, verb=f'Vous avez acheté {petits_dej} ticket(s) de petit-déjeuner')
            transaction = Transaction(description=f"Achat de {petits_dej} ticket(s) Petit-déjeuner.",tickets_pdej=petits_dej, etudiant=etudiant)
            transaction.save()
        elif petits_dej == 0 :
            dej = Ticket_Repas(nbre_tickets_repas=dejeuners,etudiant=etudiant)
            dej.save()
            notify.send(request.user, recipient=request.user, verb=f'Vous avez acheté {dejeuners} ticket(s) déjeuner')
            transaction = Transaction(description=f"Achat de {dejeuners} ticket(s) Déjeuner.",tickets_dej=dejeuners, etudiant=etudiant)
            transaction.save()
        else : 
            pdej = Ticket_Dej(nbre_tickets_dej=petits_dej,etudiant=etudiant)
            pdej.save()
            dej = Ticket_Repas(nbre_tickets_repas=dejeuners,etudiant=etudiant)
            dej.save()
            notify.send(request.user, recipient=request.user, verb=f'Vous avez acheté {petits_dej} ticket(s) de petit-déjeuner',description=f'Et {dejeuners} ticket(s) déjeuner')
            transaction = Transaction(description=f"Achat de {petits_dej} ticket(s) Petit-déjeuner et {dejeuners} ticket(s) Déjeuner.",tickets_pdej=petits_dej,tickets_dej=dejeuners, etudiant=etudiant)
            transaction.save()

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
class EtudiantLoginView(LoginView):
    template_name = "Etudiants/etudiant_login.html"
    
    def get_success_url(self):
        return reverse_lazy('home_etudiant')




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
class EtudiantDetailView(DetailView):
    context_object_name = "etudiant"
    template_name = "Etudiants/etudiant_profil.html"
    model = Etudiant
 
 
    
#Changement mot de passe
class EtudiantPasswordChangeView(PasswordChangeView):
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
def sendTicket(request):
    form = SendTicketForm()
    if request.method == 'POST':
        form = SendTicketForm(data=request.POST)
        if form.is_valid():
            code_permenant = form.cleaned_data.get('cp')
            nbreticket = form.cleaned_data.get('nbre_tickets')
            ticket_type = form.cleaned_data.get('Typeofticket')
            
            etudiantsend = Etudiant.objects.get(identifiant=request.user.identifiant)
            try:
                etudiantreceive = Etudiant.objects.get(identifiant=code_permenant)
            except Etudiant.DoesNotExist:
                messages.error(request, 'L\'étudiant récepteur n\'existe pas')
                return render(request, 'Etudiants/send_ticket.html', {'form': form})
            
             
            if ticket_type == 'dej':
                try:
                    ticketdej_sender = Ticket_Dej.objects.get(etudiant=etudiantsend)
                    if nbreticket <= ticketdej_sender.nbre_tickets_dej:
                        etudiantreceive.incrementer_ticket_dej(nbreticket)
                        etudiantsend.decrementer_ticket_dej(nbreticket)
                        nbreticket = int(nbreticket)
                        messages.success(request, f'{int(nbreticket)} Ticket(s) Petit-déjeuner envoyé(s) à {etudiantreceive.first_name} {etudiantreceive.last_name} ({etudiantreceive.identifiant}).')
                        notify.send(request.user, recipient=etudiantreceive, verb=f'Vous avez reçu {nbreticket} ticket(s) de petit-déjeuner', description=f'De la part de {etudiantsend.first_name} {etudiantsend.last_name}')
                        transactionsender = Transaction(description=f"Envoi de {nbreticket} ticket(s) Petit-déjeuner à {etudiantreceive.first_name} {etudiantreceive.last_name}.", etudiant=etudiantsend)
                        transactionsender.save()
                        transactionreceiver = Transaction(description=f"Reception de {nbreticket} ticket(s) Petit-déjeuner offert(s) par {etudiantsend.first_name} {etudiantsend.last_name}.", etudiant=etudiantreceive)
                        transactionreceiver.save()
                        return redirect('sendticket')
                    else:
                        messages.error(request, 'Nombre de tickets Petit-déjeuner insuffisant!!')
                except Ticket_Dej.DoesNotExist:
                    messages.error(request, 'Nombre de tickets Petit-déjeuner insuffisant!!')
                return redirect('sendticket')
                
                
            if ticket_type == 'repas':
                try:
                    ticketrepas_sender = Ticket_Repas.objects.get(etudiant=etudiantsend)
                    if nbreticket <= ticketrepas_sender.nbre_tickets_repas: 
                        etudiantreceive.incrementer_ticket_repas(nbreticket)
                        etudiantsend.decrementer_ticket_repas(nbreticket)
                        nbreticket = int(nbreticket)
                        messages.success(request, f'{int(nbreticket)} Ticket(s) Déjeuner envoyé(s) {etudiantreceive.first_name} {etudiantreceive.last_name} ({etudiantreceive.identifiant}).')
                        notify.send(request.user, recipient=etudiantreceive, verb=f'Vous avez reçu {nbreticket} ticket(s) de déjeuner', description=f'De la part de {etudiantsend.first_name} {etudiantsend.last_name}')
                        transactionsender = Transaction(description=f"Envoi de {nbreticket} ticket(s) Déjeuner à {etudiantreceive.first_name} {etudiantreceive.last_name}.", etudiant=etudiantsend)
                        transactionsender.save()
                        transactionreceiver = Transaction(description=f"Reception de {nbreticket} ticket(s) Déjeuner offert(s) par {etudiantsend.first_name} {etudiantsend.last_name}.", etudiant=etudiantreceive)
                        transactionreceiver.save()
                        return redirect('sendticket')
                    else:
                        messages.error(request, 'Nombre de tickets Déjeuner insuffisant!!')            
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
class EtudiantViewset(ModelViewSet):
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
            etudiant = Etudiant.objects.get(identifiant=pk)
        except Etudiant.DoesNotExist:
            return Response({'error': 'Etudiant(e) non trouve'},
                    status=status.HTTP_404_NOT_FOUND)
        
        
        heure = datetime.datetime.now().hour
        
        
        #decrementer ticket dej
        if (heure)>=6 and int(heure)<=11:
            try:
                ticketDej =  Ticket_Dej.objects.get(etudiant=etudiant)
                if ticketDej.nbre_tickets_dej > 0:
                    etudiant.decrementer_ticket_dej(1)
                    #transaction = Transaction(description=f"Consommation d'un ticket Petit-déjeuner.", etudiant=etudiant)
                    #transaction.save()
                    return Response({"message": "Decrementation reussie!!","code_permenant": ticketDej.etudiant.identifiant})
                else:
                    return Response({"error": "Aucun ticket petit-dejeuner!!"}, status=status.HTTP_404_NOT_FOUND)
            except Ticket_Dej.DoesNotExist:
                return Response({'error': 'Aucun ticket petit-dejeuner!!'},
                    status=status.HTTP_404_NOT_FOUND)
        
        
        #decrementer ticket repas  
        elif (heure)>=12 and (heure)<=17 or (heure)>=0 and int(heure)<=23:
                try:
                    ticketRepas =  Ticket_Repas.objects.get(etudiant=etudiant)
                    if ticketRepas.nbre_tickets_repas > 0:
                        etudiant.decrementer_ticket_repas(1)
                        #transaction = Transaction(description=f"Consommation d'un ticket déjeuner.", etudiant=etudiant)
                        #transaction.save()
                        return Response({"message": "Decrementation reussie!!","code_permenant": ticketRepas.etudiant.identifiant})
                    else:
                        return Response({"error": "Aucun ticket dejeuner!!"}, status=status.HTTP_404_NOT_FOUND)
                except Ticket_Repas.DoesNotExist:
                    return Response({"error": "Aucun ticket dejeuner!!"},
                    status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"error": "Hors delai!!"}, status=status.HTTP_404_NOT_FOUND)
              
        # Sérialiser les détails de l'étudiant
        serializer = self.get_serializer(etudiant)
        # Retourner les détails de l'étudiant dans la réponse
        return Response(serializer.data)
    
    
                        
    
    
                        
    # def partial_update(self, request,cp=None):
    #      etudiant = self.get_queryset().get(code_permenant=cp)
    #      etudiant.decrementer_ticket_repas();
        
    #      serializer = EtudiantSerializer(etudiant)
    #      return Response(serializer.data)
    
    
    

        
    

