from django.urls import include, path

from Personnels import views









urlpatterns = [
    path('',views.Personnel_loginView.as_view(),name='personnel-login'),
    path('personnel_accueil/',views.home_personnel,name='personnel-home'),
    path('<int:pk>/etudiantdetail/',views.EtudiantDetail.as_view(),name='etudiantdetail'),
    path('vente/',views.personnel_graphic,name='vente'), 
    path('personnel_deconnexion/',views.personnel_deconnected,name='personnel-deconnexion'), 
         
]