from django.contrib import admin

from Admin.models import User
from Personnels.models import Personnel

# Register your models here.




@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display=('first_name','last_name','is_superuser','is_personnel','is_etudiant')
    list_filter=('is_superuser',)
    search_fields=('identifiant',)