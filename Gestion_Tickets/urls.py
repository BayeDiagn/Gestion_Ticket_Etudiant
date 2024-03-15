from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

import Etudiants






urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include("Etudiants.urls")),
    path('api/', include("Tickets.urls")),
    
    
    path('api-auth/', include('rest_framework.urls')),
    
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)