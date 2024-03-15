from django.urls import include, path


from rest_framework import routers

from Tickets import views




router_repas = routers.SimpleRouter()
router_repas.register('', views.TicketRepasViewset, basename='ticket_repas')
router_dej = routers.SimpleRouter()
router_dej.register('', views.TicketDejViewset, basename='ticket_repas')

urlpatterns = [
    path('ticket_repas/',include(router_repas.urls)),
    path('ticket_dej/',include(router_dej.urls)),
]