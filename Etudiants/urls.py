from django.urls import include, path

from Etudiants import views
from django.contrib.auth.views import PasswordResetConfirmView

from rest_framework import routers
import notifications.urls




router = routers.SimpleRouter()
router.register('etudiant', views.EtudiantViewset, basename='etudiant')
routerPers = routers.SimpleRouter()
routerPers.register('personnel', views.TicketConsommerViewset, basename='personnel')

urlpatterns = [
    path('',views.EtudiantLoginView.as_view(), name='login_etudiant'),
    # path('inscription/',views.EtudiantCreateView.as_view(), name='signup_etudiant'),
    path('accueil/',views.etudiant_home, name='home_etudiant'),
    path('send_ticket/',views.sendTicket, name='sendticket'),
    path('deconnexion/',views.etudiant_deconnected, name='deconnected_etudiant'),
    path('<int:pk>/detail_etudiant/',views.EtudiantDetailView.as_view(), name='detail_etudiant'),
    path('transaction/',views.etudiant_transaction, name='transaction_etudiant'),
    path('<int:pk>/changepassword/',views.EtudiantPasswordChangeView.as_view(), name='passwordchanged_etudiant'),
    path('<int:pk>/change_qrcode/',views.changeQrCode, name='etudiant_change_qrcode'),
    
    path("etudiant_resetpassword/",views.MyPasswordRestView.as_view(),name="password_reset"),
    path("etudiant_mailSend/",views.MyPasswordResetDoneView.as_view(),name="password_reset_done"),
    path("password_confirm/<uidb64>/<token>/",PasswordResetConfirmView.as_view(template_name='Etudiants/passwordChanged.html'),name="password_reset_confirm"),
    path('password_complete/',views.EtudiantPasswordResetCompleteView.as_view(),name='password_reset_complete'),
    
    path('payment-done/',views.payment_done, name='payment_done'),
    path('payment-canceled/',views.payment_canceled, name='payment_canceled'),
    path('clear_notification/',views.clear_notification, name='clear_notification'),
    #path('^inbox/notifications/', include(notifications.urls, namespace='notifications')),
    
    #path("password_complete/",PasswordResetCompleteView.as_view(template_name='Etudiants/etudiant_passwordComplet.html'),name="password_changed"),
    #path('api/etudiant/',views.EtudiantAPIView.as_view()),
    path('api/etudiant/<str:pk>/', views.EtudiantViewset.as_view({'get': 'retrieve_by_code_permanent'}), name='etudiant-detail'),
    path('api/consommer/<str:pk>/', views.TicketConsommerViewset.as_view(), name='consommer-ticket'),
    path('api/',include(router.urls)),
]