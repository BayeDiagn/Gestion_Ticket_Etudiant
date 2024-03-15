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


#def automatiser_code():
 #   camera = True
  #  cap = cv2.VideoCapture(0)

   # while camera:
    #    start_time = time.time()

     #   success, frame = cap.read()

      #  for elmt in decode(frame):
       #     print(elmt.type)
        #    print(elmt.data.decode('utf-8'))

         #   etudiant = Etudiant.objects.get(code_permenant=elmt.data.decode('utf-8'))

          #  date = datetime.now()
           # heure = date.strftime('%H')

            #if int(heure) >= 6 and int(heure) <= 11:
                #etudiant.decrementer_ticket_dej()

            #if (int(heure) >= 0 and int(heure) <= 24) or (int(heure) >= 18 and int(heure) <= 21):
               # etudiant.decrementer_ticket_repas()

        #cv2.imshow('testing code scan', frame)
        #cv2.waitKey(1)

        #end_time = time.time()
        #elapsed_time = end_time - start_time
        #if elapsed_time < 0.001:
         #   time.sleep(0.001 - elapsed_time)


#while True:
 #   automatiser_code()
 
 
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