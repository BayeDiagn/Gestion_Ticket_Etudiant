from django.urls import include, path

from Personnels import views









urlpatterns = [
    path('',views.home_personnel,name='personnel-home'),
    path('<int:pk>/etudiantdetail/',views.EtudiantDetail.as_view(),name='etudiantdetail'),
    path('vente/',views.personnel_graphic,name='vente'),
         
]