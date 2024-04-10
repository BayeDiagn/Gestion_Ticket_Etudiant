import random
from django.shortcuts import redirect, render
from datetime import date, timedelta
from django.utils import timezone
from calendar import monthrange
from django.db.models import Sum
from django.views.generic import DetailView
from django.core.paginator import Paginator
from django.contrib.auth.views import LoginView
from django.contrib.auth import  logout,get_user_model
from django.contrib.auth.decorators import login_required,user_passes_test
from django.urls import reverse_lazy
from django.contrib import messages

from Etudiants.models import Etudiant, Transaction
from Personnels.models import Personnel, TicketConsommer
from django.shortcuts import get_object_or_404, redirect
from rest_framework.views import APIView
from Personnels.serializers import TicketConsommerSerializer
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework import status










#Personnel Login
class Personnel_loginView(LoginView):
    template_name = "Personnels/personnel_login.html"
    
    def get_success_url(self):
        return reverse_lazy('personnel-home')
    
    
#Personnel deconnexion
def personnel_deconnected(request):
    logout(request)
    
    return redirect("personnel-login")


#Decorator pour Personnel
def personnel_required(view_func):
    decorated_view_func = user_passes_test(
        lambda user: user.is_authenticated and user.is_personnel,
        login_url='personnel-login'
    )(view_func)
    return decorated_view_func



#Home Personnel
@personnel_required
def home_personnel(request):
    
    #Aujourd'hui
    aujourdhui = date.today()
    
    personnel = Personnel.objects.get(identifiant=request.user.identifiant)
    tickets_pdej_consommes_aujourd_hui = personnel.tickets.filter(type_ticket='pdej',date=aujourdhui).aggregate(Sum('quantity'))['quantity__sum'] or 0
    tickets_dej_consommes_aujourd_hui = personnel.tickets.filter(type_ticket='dej',date=aujourdhui).aggregate(Sum('quantity'))['quantity__sum'] or 0
    tickets_dinner_consommes_aujourd_hui = personnel.tickets.filter(type_ticket='dinner',date=aujourdhui).aggregate(Sum('quantity'))['quantity__sum'] or 0
    
    montant_total_jour = (50*tickets_pdej_consommes_aujourd_hui) + (100*tickets_dej_consommes_aujourd_hui) + (100*tickets_dinner_consommes_aujourd_hui)

    #Semaine
    debut_semaine = aujourdhui - timedelta(days=aujourdhui.weekday())
    fin_semaine = debut_semaine + timedelta(days=6)

    tickets_pdej_of_week = personnel.tickets.filter(type_ticket='pdej', date__range=(debut_semaine, fin_semaine)).aggregate(Sum('quantity'))['quantity__sum'] or 0
    tickets_dej_of_week = personnel.tickets.filter(type_ticket='dej', date__range=(debut_semaine, fin_semaine)).aggregate(Sum('quantity'))['quantity__sum'] or 0
    tickets_diner_of_week = personnel.tickets.filter(type_ticket='dinner', date__range=(debut_semaine, fin_semaine)).aggregate(Sum('quantity'))['quantity__sum'] or 0
    
    montant_total_week = (50*tickets_pdej_of_week) + (100*tickets_dej_of_week) + (100*tickets_diner_of_week)
    
    #Mois
    # Récupérer le premier et le dernier jour du mois en cours
    premier_jour_mois = date(aujourdhui.year, aujourdhui.month, 1)
    dernier_jour_mois = date(aujourdhui.year, aujourdhui.month, monthrange(aujourdhui.year, aujourdhui.month)[1])
    
    tickets_pdej_of_currentmonth = personnel.tickets.filter(type_ticket='pdej', date__range=(premier_jour_mois, dernier_jour_mois)).aggregate(Sum('quantity'))['quantity__sum'] or 0
    tickets_dej_of_currentmonth = personnel.tickets.filter(type_ticket='dej', date__range=(premier_jour_mois, dernier_jour_mois)).aggregate(Sum('quantity'))['quantity__sum'] or 0
    tickets_diner_of_currentmonth = personnel.tickets.filter(type_ticket='dinner', date__range=(premier_jour_mois, dernier_jour_mois)).aggregate(Sum('quantity'))['quantity__sum'] or 0
    
    montant_total_mois = (50*tickets_pdej_of_currentmonth ) + (100*tickets_dej_of_currentmonth ) + (100*tickets_diner_of_currentmonth )
    #total = montant_total_week + montant_total_mois
    
    #Annees
    # Récupérer le premier et le dernier jour de l'année en cours
    premier_jour_annee = date(aujourdhui.year, 1, 1)
    dernier_jour_annee = date(aujourdhui.year, 12, 31)

    # Récupérer les quantités de tickets consommés pendant toute l'année pour chaque type de ticket
    tickets_pdej_of_year = personnel.tickets.filter(type_ticket='pdej', date__range=(premier_jour_annee, dernier_jour_annee)).aggregate(Sum('quantity'))['quantity__sum']
    tickets_dej_of_year = personnel.tickets.filter(type_ticket='dej', date__range=(premier_jour_annee, dernier_jour_annee)).aggregate(Sum('quantity'))['quantity__sum']
    tickets_diner_of_year = personnel.tickets.filter(type_ticket='dinner', date__range=(premier_jour_annee, dernier_jour_annee)).aggregate(Sum('quantity'))['quantity__sum']

    # Calculer le montant total des tickets consommés pendant l'année
    montant_total_year = (50 * tickets_pdej_of_year) + (100 * tickets_dej_of_year) + (100 * tickets_diner_of_year) 
   
    
    #liste Etudiant
    etudiants = Etudiant.objects.all().order_by('identifiant')
    p=Paginator( etudiants,10)
    page=request.GET.get('page')
    liste=p.get_page(page)
    
    

    colors = [
        "#"+''.join([random.choice('0123456789ABCDEF') for j in range(6)])  
        for i in range(3)
    ]

    
    context = {"nbreTPD":int(tickets_pdej_consommes_aujourd_hui),"nbreTRP":int(tickets_dej_consommes_aujourd_hui),
                "nbreTD":int(tickets_dinner_consommes_aujourd_hui),"colors":colors,"montant_total_jour":montant_total_jour,
                "montant_total_week":montant_total_week,"montant_total_mois":montant_total_mois,"tickets_pdej_of_week":
                 int(tickets_pdej_of_week),"tickets_dej_of_week":int(tickets_dej_of_week ),
                 "tickets_diner_of_week":int(tickets_diner_of_week ),"ticket_pdej_month":int(tickets_pdej_of_currentmonth),
                 "ticket_dej_month":int(tickets_dej_of_currentmonth),"ticket_diner_month":int(tickets_diner_of_currentmonth),
                 "liste":liste,"tickets_pdej_of_year":tickets_pdej_of_year,"tickets_dej_of_year":tickets_dej_of_year,
                 "tickets_diner_of_year":tickets_diner_of_year,"montant_total_year":montant_total_year,
                }
    return render(request,'Personnels/home_personnel.html',context)



#Achat Etudiant
@personnel_required
def personnel_graphic(request):
    
    # Récupérer la date d'aujourd'hui
    aujourdhui = date.today()
    ticket_pdej_achat_today = Transaction.objects.filter(description__icontains='Achat',date=aujourdhui).exclude(tickets_pdej=0).aggregate(Sum('tickets_pdej'))['tickets_pdej__sum'] or 0
    ticket_dej_achat_today = Transaction.objects.filter(description__icontains='Achat',date=aujourdhui).exclude(tickets_dej=0).aggregate(nbre_dej=Sum('tickets_dej'))['nbre_dej'] or 0
    
    montant_pdej_today = 50*ticket_pdej_achat_today
    montant_dej_today = 100*ticket_dej_achat_today
    montant_today = montant_pdej_today + montant_dej_today
    
    #Semaine
    debut_semaine = aujourdhui - timedelta(days=aujourdhui.weekday())
    fin_semaine = debut_semaine + timedelta(days=6)
    
    ticket_pdej_achat_week = Transaction.objects.filter(description__icontains='Achat',date__range=(debut_semaine, fin_semaine)).exclude(tickets_pdej=0).aggregate(Sum('tickets_pdej'))['tickets_pdej__sum'] or 0
    ticket_dej_achat_week = Transaction.objects.filter(description__icontains='Achat',date__range=(debut_semaine, fin_semaine)).exclude(tickets_dej=0).aggregate(nbre_dej=Sum('tickets_dej'))['nbre_dej'] or 0
    
    montant_pdej_week = 50*ticket_pdej_achat_week
    montant_dej_week = 100*ticket_dej_achat_week
    montant_week = montant_pdej_week + montant_dej_week
    
    #Mois
    # Récupérer le premier et le dernier jour du mois en cours
    premier_jour_mois = date(aujourdhui.year, aujourdhui.month, 1)
    dernier_jour_mois = date(aujourdhui.year, aujourdhui.month, monthrange(aujourdhui.year, aujourdhui.month)[1])
    
    ticket_pdej_achat_mois = Transaction.objects.filter(description__icontains='Achat',date__range=(premier_jour_mois,dernier_jour_mois)).exclude(tickets_pdej=0).aggregate(Sum('tickets_pdej'))['tickets_pdej__sum'] or 0
    ticket_dej_achat_mois = Transaction.objects.filter(description__icontains='Achat',date__range=(premier_jour_mois, dernier_jour_mois)).exclude(tickets_dej=0).aggregate(nbre_dej=Sum('tickets_dej'))['nbre_dej'] or 0
    
    montant_pdej_mois = 50*ticket_pdej_achat_mois
    montant_dej_mois = 100*ticket_dej_achat_mois
    montant_mois = montant_pdej_mois + montant_dej_mois
    
    
    #Annees
    # Récupérer le premier et le dernier jour de l'année en cours
    premier_jour_annee = date(aujourdhui.year, 1, 1)
    dernier_jour_annee = date(aujourdhui.year, 12, 31)
    
    ticket_pdej_achat_annee = Transaction.objects.filter(description__icontains='Achat',date__range=(premier_jour_annee, dernier_jour_annee)).exclude(tickets_pdej=0).aggregate(Sum('tickets_pdej'))['tickets_pdej__sum'] or 0
    ticket_dej_achat_annee = Transaction.objects.filter(description__icontains='Achat',date__range=(premier_jour_annee, dernier_jour_annee)).exclude(tickets_dej=0).aggregate(nbre_dej=Sum('tickets_dej'))['nbre_dej'] or 0
    
    montant_pdej_annee = 50*ticket_pdej_achat_annee
    montant_dej_annee = 100*ticket_dej_achat_annee
    montant_annee = montant_pdej_annee + montant_dej_annee
    
    
    color = [
        "#"+''.join([random.choice('0123456789ABCDEF') for j in range(6)])  
        for i in range(3)
    ]
    colors = [
        "#"+''.join([random.choice('456789ABCDEF0123') for j in range(6)])  
        for i in range(3)
    ]
    
    context = {"colors":colors,"color":color,"ticket_pdej_achat_today":ticket_pdej_achat_today,"ticket_dej_achat_today":ticket_dej_achat_today,
               "montant_pdej_today":montant_pdej_today,"montant_dej_today":montant_dej_today,"montant_today":montant_today,
               "ticket_pdej_achat_week":ticket_pdej_achat_week,"ticket_dej_achat_week":ticket_dej_achat_week,"montant_week": montant_week,
               "montant_pdej_week":montant_pdej_week,"montant_dej_week":montant_dej_week,"ticket_pdej_achat_mois":ticket_pdej_achat_mois,
               "ticket_dej_achat_mois":ticket_dej_achat_mois,"montant_pdej_mois": montant_pdej_mois,"montant_dej_mois": montant_dej_mois,
               "montant_mois": montant_mois,"ticket_pdej_achat_annee":ticket_pdej_achat_annee,"ticket_dej_achat_annee":ticket_dej_achat_annee,
               "montant_pdej_annee":montant_pdej_annee,"montant_dej_annee":montant_dej_annee,"montant_annee":montant_annee
               }   
    
    return render(request,'Personnels/personnel_vente.html',context)





#Detail Etudiant
#@personnel_required
class EtudiantDetail(DetailView):
    model = Etudiant
    template_name='Personnels/details_etudiants.html'
    
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Récupérer l'ID de l'étudiant
        etudiant_id = self.object.pk

        # Récupérer la date d'aujourd'hui
        aujourdhui = date.today()
        
         #Mois
        # Récupérer le premier et le dernier jour du mois en cours
        premier_jour_mois = date(aujourdhui.year, aujourdhui.month, 1)
        dernier_jour_mois = date(aujourdhui.year, aujourdhui.month, monthrange(aujourdhui.year, aujourdhui.month)[1])
    
        ticket_pdej_achat_mois = Transaction.objects.filter(etudiant=etudiant_id,description__icontains='Achat',date__range=(premier_jour_mois,dernier_jour_mois)).exclude(tickets_pdej=0).aggregate(Sum('tickets_pdej'))['tickets_pdej__sum'] or 0
        ticket_dej_achat_mois = Transaction.objects.filter(etudiant=etudiant_id,description__icontains='Achat',date__range=(premier_jour_mois, dernier_jour_mois)).exclude(tickets_dej=0).aggregate(nbre_dej=Sum('tickets_dej'))['nbre_dej'] or 0
        
        montant_pdej_mois = 50*ticket_pdej_achat_mois
        montant_dej_mois = 100*ticket_dej_achat_mois
        montant_mois = montant_pdej_mois + montant_dej_mois
        
        
        #Annees
        # Récupérer le premier et le dernier jour de l'année en cours
        premier_jour_annee = date(aujourdhui.year, 1, 1)
        dernier_jour_annee = date(aujourdhui.year, 12, 31)
    
        ticket_pdej_achat_annee = Transaction.objects.filter(etudiant=etudiant_id,description__icontains='Achat',date__range=(premier_jour_annee, dernier_jour_annee)).exclude(tickets_pdej=0).aggregate(Sum('tickets_pdej'))['tickets_pdej__sum'] or 0
        ticket_dej_achat_annee = Transaction.objects.filter(etudiant=etudiant_id,description__icontains='Achat',date__range=(premier_jour_annee, dernier_jour_annee)).exclude(tickets_dej=0).aggregate(nbre_dej=Sum('tickets_dej'))['nbre_dej'] or 0
    
        montant_pdej_annee = 50*ticket_pdej_achat_annee
        montant_dej_annee = 100*ticket_dej_achat_annee
        montant_annee = montant_pdej_annee + montant_dej_annee
        
        
        colors = [
            "#"+''.join([random.choice('456789ABCDEF0123') for j in range(6)])  
            for i in range(3)
        ]
        
        context.update({
            "ticket_pdej_achat_mois":ticket_pdej_achat_mois,"ticket_dej_achat_mois":ticket_dej_achat_mois,
            "montant_pdej_mois":montant_pdej_mois,"montant_dej_mois":montant_dej_mois,"montant_mois":montant_mois,
            "ticket_pdej_achat_annee":ticket_pdej_achat_annee,"ticket_dej_achat_annee":ticket_dej_achat_annee,
            "montant_pdej_annee":montant_pdej_annee,"montant_dej_annee":montant_dej_annee,"montant_annee":montant_annee,
            "colors":colors
        })

        
        return context
    
    

#boquer un compte etudiant
User = get_user_model()

def block_Etudiant(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    if user.is_active == True:
        user.is_active = False
        user.save()
        messages.error(request, 'Etudiant(e) bloqué(e)!!')
    else:
        messages.info(request, "Ce compte a été bloqué !") 
    return redirect('etudiantdetail',user_id)


#debloquer un compte etudiant
def unblock_Etudiant(request,user_id):
    user = get_object_or_404(User, pk=user_id)
    if user.is_active == False:
        user.is_active = True
        user.save()
        messages.success(request, 'Etudiant(e) débloqué(e)!!')  
    else:
        messages.info(request, "Ce compte n'était pas bloqué !") 
    return redirect('etudiantdetail',user_id)




#TicketConsommer
# class TicketConsommerViewset(ModelViewSet):
#     serializer_class = TicketConsommerSerializer
#      #queryset = Etudiant.objects.all()
    
#     def get_queryset(self):
#          queryset = Personnel.objects.all()  
#          return queryset
    
#     def create(self, request):
#         identifiant = request.data.get('identifiant')
#         type_ticket = request.data.get('type_ticket')
#         quantity = request.data.get('quantity')
        
#         try:
#             personnel = Personnel.objects.get(identifiant=identifiant)
#         except Personnel.DoesNotExist:
#             return Response({'error': 'Personnel non trouvé'}, status=status.HTTP_404_NOT_FOUND)
            
#         ticket = TicketConsommer(type_ticket=type_ticket, quantity=quantity, personnel=personnel)
#         ticket.save()
#         serializer = TicketConsommerSerializer(ticket)
#         return Response(serializer.data, status=status.HTTP_201_CREATED)