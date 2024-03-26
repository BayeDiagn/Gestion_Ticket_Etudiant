from django.contrib import admin

from Personnels.models import Personnel

# Register your models here.


@admin.register(Personnel)
class Personnel(admin.ModelAdmin):
    list_display=('identifiant','first_name','last_name','email','is_personnel','date_joined')
    list_filter=('first_name',)
    search_fields=('identifiant',)