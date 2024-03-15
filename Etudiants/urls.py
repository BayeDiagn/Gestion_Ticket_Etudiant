from django.urls import include, path

from Etudiants import views
from django.contrib.auth.views import PasswordResetCompleteView

from rest_framework import routers




router = routers.SimpleRouter()
router.register('etudiant', views.EtudiantViewset, basename='etudiant')

urlpatterns = [
    path('',views.EtudiantLoginView.as_view(), name='login_etudiant'),
    path('accueil/',views.etudiant_home, name='home_etudiant'),
    path('deconnexion/',views.etudiant_deconnected, name='deconnected_etudiant'),
    path('<int:pk>/detail_etudiant/',views.EtudiantDetailView.as_view(), name='detail_etudiant'),
    path('transaction/',views.etudiant_transaction, name='transaction_etudiant'),
    path('<int:pk>/changepassword/',views.EtudiantPasswordChangeView.as_view(), name='passwordchanged_etudiant'),
    path('password_complete/',views.EtudiantPasswordResetCompleteView.as_view(),name='password_changed'),
    #path("password_complete/",PasswordResetCompleteView.as_view(template_name='Etudiants/etudiant_passwordComplet.html'),name="password_changed"),
    #path('api/etudiant/',views.EtudiantAPIView.as_view()),
    path('api/etudiant/<str:pk>/', views.EtudiantViewset.as_view({'get': 'retrieve_by_code_permanent'}), name='etudiant-detail'),
    path('api/',include(router.urls)),
]