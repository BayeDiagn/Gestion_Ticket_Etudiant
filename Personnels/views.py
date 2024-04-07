import random
from django.shortcuts import render
from datetime import date, timedelta
from calendar import monthrange
from django.db.models import Sum
from django.views.generic import DetailView
from django.core.paginator import Paginator

from Etudiants.models import Etudiant
from Personnels.models import Personnel









def home_personnel(request):
    
    #Aujourd'hui
    aujourdhui = date.today()
    
    personnel = Personnel.objects.get(identifiant="restau_campus1")
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



#Detail Etudiant
class EtudiantDetail(DetailView):
    model = Etudiant
    template_name='Personnels/details_etudiants.html'
    








def personnel_graphic(request):
    
    personnel = Personnel.objects.get(identifiant="restau_campus1")
    
    # Récupérer la date d'aujourd'hui
    aujourdhui = date.today()


    
    
    
    colors = [
        "#"+''.join([random.choice('0123456789ABCDEF') for j in range(6)])  
        for i in range(3)
    ]
    
    context = {"colors":colors,}   
    
    return render(request,'Personnels/personnel_vente.html',context)