from django.urls import include, path

from Personnels import views
from rest_framework import routers






# router = routers.SimpleRouter()
# router.register('personnel', views.TicketConsommerViewset, basename='personnel')

urlpatterns = [
    path('',views.Personnel_loginView.as_view(),name='personnel-login'),
    path('personnel_accueil/',views.home_personnel,name='personnel-home'),
    path('<int:pk>/etudiantdetail/',views.EtudiantDetail.as_view(),name='etudiantdetail'),
    path('vente/',views.personnel_graphic,name='vente'), 
    path('personnel_deconnexion/',views.personnel_deconnected,name='personnel-deconnexion'), 
    path('etudiant/<int:user_id>/block/', views.block_Etudiant, name='block_etudiant'),
    path('etudiant/<int:user_id>/unblock/', views.unblock_Etudiant, name='unblock_etudiant'),
    
    # path('api/consommer/', views.TicketConsommerViewset.as_view(), name='consommer-ticket'),
    # path('api/',include(router.urls)),
         
]