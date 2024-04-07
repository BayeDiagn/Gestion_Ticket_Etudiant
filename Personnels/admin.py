from django.contrib import admin

from Personnels.models import Personnel, TicketConsommer

# Register your models here.

class Ticket_Consommer(admin.TabularInline):
    model = TicketConsommer
    extra=0

@admin.register(Personnel)
class Personnel(admin.ModelAdmin):
    list_display=('identifiant','first_name','last_name','email','is_personnel','date_joined')
    list_filter=('first_name',)
    search_fields=('identifiant',)
    inlines=(Ticket_Consommer,)