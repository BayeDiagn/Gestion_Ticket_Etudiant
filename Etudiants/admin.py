from django.contrib import admin

from Etudiants.models import Etudiant
from Tickets.models import Ticket_Dej, Ticket_Repas










class Ticket_Repas_Add(admin.TabularInline):
    model=Ticket_Repas
    extra=0


class Ticket_Dej_Add(admin.TabularInline):
    model=Ticket_Dej
    extra=0



@admin.register(Etudiant)
class Etudiants(admin.ModelAdmin):
    list_display=('identifiant','first_name','last_name','email','is_etudiant','date_joined')
    list_filter=('identifiant','first_name','last_name')
    search_fields=('identifiant', )
    ordering = ('identifiant',)
    list_per_page = 5
    inlines=(Ticket_Repas_Add, Ticket_Dej_Add)


