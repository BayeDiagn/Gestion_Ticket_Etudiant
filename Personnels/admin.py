from django.contrib import admin

from Personnels.models import Personnel

# Register your models here.


@admin.register(Personnel)
class Personnel(admin.ModelAdmin):
    list_display=('first_name','last_name','email','is_personnel')
    #list_filter=()
    search_fields=('email',)