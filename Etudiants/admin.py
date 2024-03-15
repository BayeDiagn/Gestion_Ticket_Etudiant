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
    list_display=('identifiant','first_name','last_name','email','is_etudiant')
    #list_filter=('code_permenant','first_name','last_name','email',)
    search_fields=('identifiant', )
    inlines=(Ticket_Repas_Add, Ticket_Dej_Add)


