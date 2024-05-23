from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.conf.urls import handler404







urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include("Etudiants.urls")),
    path('personnel/', include("Personnels.urls")),
    path('api/', include("Tickets.urls")),
    
    
    path('api-auth/', include('rest_framework.urls')),
    
    
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# handler404 = "Admin.views.notFoundPage"