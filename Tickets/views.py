from django.shortcuts import render

import datetime
import time
import cv2
from pyzbar.pyzbar import decode
from django.shortcuts import render
import qrcode

from Etudiants.models import Etudiant
from Tickets.models import Ticket_Dej, Ticket_Repas
from Tickets.serializers import DejSerializer, RepaSerializer
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet


# Create your views here.





 
 
class TicketRepasViewset(ModelViewSet):
    
    serializer_class = RepaSerializer
     

    def get_queryset(self):
        queryset = Ticket_Repas.objects.all()
        return queryset
    

class TicketDejViewset(ModelViewSet):
    
    serializer_class = DejSerializer
     

    def get_queryset(self):
        queryset = Ticket_Dej.objects.all()
        return queryset