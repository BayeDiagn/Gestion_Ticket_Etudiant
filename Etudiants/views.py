import datetime
import cv2
from django.urls import reverse_lazy
from pyzbar.pyzbar import decode
from django.shortcuts import redirect, render
import qrcode
from django.db.models import Count,Sum

from Etudiants.models import Etudiant

from rest_framework.views import APIView
from Etudiants.serializers import EtudiantSerializer
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework import status
from django.contrib.auth.views import LoginView,PasswordChangeView,PasswordResetCompleteView,PasswordResetView,PasswordResetDoneView
from django.views.generic import DetailView
from django.contrib.auth.decorators import login_required,user_passes_test
from django.utils.decorators import method_decorator
from django.contrib.auth import  logout

from Tickets.models import Ticket_Dej, Ticket_Repas






#decorateur controlant l'acces a la page accueil
def etudiant_required(view_func):
    decorated_view_func = user_passes_test(
        lambda user: user.is_authenticated and user.is_etudiant,
        login_url='login_etudiant'
    )(view_func)
    return decorated_view_func


#Accueil
@etudiant_required
@login_required
def etudiant_home(request):
    
    etudiant = Etudiant.objects.get(id=request.user.id)
    
    tickets_dej_etudiant = Ticket_Dej.objects.filter(etudiant=etudiant)
    nbre_tickets_dej = int(sum(ticket.nbre_tickets_dej for ticket in tickets_dej_etudiant))
    
    tickets_repas_etudiant = Ticket_Repas.objects.filter(etudiant=etudiant)
    nbre_tickets_repas = int(sum(ticket.nbre_tickets_repas for ticket in tickets_repas_etudiant))
    
    #print(nbre_total_tickets_dej)
    
    #img = qrcode.make('1505378')
    #img.save('code_p.png')
    #Cap = cv2.VideoCapture(0)
    #Cap.set(5,640)
    #Cap.set(6,480)
    
    #camera = True
    #while camera == True:
        #success , frame = Cap.read()
        #for elmt in decode(frame):
            #print(elmt.type)
           # print(elmt.data.decode('utf-8'))
            
            
           # etudiant = Etudiant.objects.get(code_permenant=elmt.data.decode('utf-8'))
            #date = datetime.datetime.now()
    #         heure=date.strftime('%H')
            
    #         #print(heure)
    #         if int(heure) >= 6 and int(heure) <= 11:
    #             etudiant.decrementer_ticket_dej()
        
    #         if (int(heure) >= 12 and int(heure) <= 14) or (int(heure) >= 18 and int(heure) <= 21):
    #                 etudiant.decrementer_ticket_repas()
    #         time.sleep(5)
    
    # #print(etudiant.code_qr.url)
    # #print(etudiant.code_qr.path)
    
    #         cv2.imshow('testing code scan', frame)
    #         cv2.waitKey(3)
                
    #etudiant = Etudiant.objects.get(id=6)
    #d = cv2.QRCodeDetector()
 
    #Val , points , data = d.detectAndDecode(cv2.imread(etudiant.code_qr.path))
    #print(Val)
    
    
    
    context = {"nbre_tickets_dej":nbre_tickets_dej,"nbre_tickets_repas":nbre_tickets_repas}
    return render(request,'Etudiants/etudiant_home.html',context)

#login
class EtudiantLoginView(LoginView):
    template_name = "Etudiants/etudiant_login.html"
    
    def get_success_url(self):
        return reverse_lazy('home_etudiant')


#view de deconnexion
def etudiant_deconnected(request):
    logout(request)
    
    return redirect("login_etudiant")


#Detail_etudiant
class EtudiantDetailView(DetailView):
    context_object_name = "etudiant"
    template_name = "Etudiants/etudiant_profil.html"
    model = Etudiant
 
    
#Changement mot de passe
class EtudiantPasswordChangeView(PasswordChangeView):
    template_name = "Etudiants/etudiant_changedPassword.html"
    success_url=reverse_lazy('password_reset_complete')


#Page vue apres changement
#@method_decorator(etudiant_required, name='dispatch')
class EtudiantPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = "Etudiants/etudiant_passwordComplet.html"
    
    


#Transaction User
@etudiant_required
@login_required
def etudiant_transaction(request):
    
    
    
    context = {}
    return render(request,'Etudiants/etudiant_transaction.html',context)



class MyPasswordRestView(PasswordResetView):
    template_name='Etudiants/etudiant_resetPassword.html'
    #success_url = reverse_lazy('password_reset_complete')
    

class MyPasswordResetDoneView(PasswordResetDoneView):
    #form_class=PasswordResetForm
    template_name='Etudiants/etudiant_emailSend.html'
    



#API
# class EtudiantAPIView(APIView):
    
#     def get(self,request):
#         etudiants = Etudiant.objects.all().order_by('code_permenant')
#         serializer = EtudiantSerializer(etudiants, many=True)
#         return Response(serializer.data)
    
    
    
    
#Autre façon API 
class EtudiantViewset(ModelViewSet):
    serializer_class = EtudiantSerializer
    #queryset = Etudiant.objects.all()
    
    def get_queryset(self):
         queryset = Etudiant.objects.all()  #annotate(nbre_tickets_repas=Count('ticket_repas')).values('id', 'code_permenant', 'first_name', 'last_name', 'nbre_tickets_repas')
         return queryset
    
    
    
    #requete vers l'api 
    @action(detail=False, methods=['get'])
    def retrieve_by_code_permanent(self, request, pk=None):
        # Récupérer l'étudiant en fonction de son code permanent
        try:
            etudiant = Etudiant.objects.get(identifiant=pk)
        except Etudiant.DoesNotExist:
            return Response({'error': 'Étudiant(e) non trouvé'},
                    status=status.HTTP_404_NOT_FOUND)
        
        
        date = datetime.datetime.now()
        heure = date.strftime('%H')
        #mn = date.strftime('%M')
        
        
        #decrementer ticket dej
        if(int(heure)>=6 and int(heure)<=13):
            try:
                ticketDej =  Ticket_Dej.objects.get(etudiant=etudiant)
                if ticketDej.nbre_tickets_dej > 0:
                    etudiant.decrementer_ticket_dej()
                    return Response({"message": "Décrémentation réussie","code_permenant": ticketDej.etudiant.identifiant})
                else:
                    return Response({"error": "Pas de tickets déjeuner pour cet(te) étudiant(e)"}, status=status.HTTP_404_NOT_FOUND)
            except Ticket_Dej.DoesNotExist:
                return Response({'error': 'Pas de tickets déjeuner pour cet(te) etudiant(e)'},
                    status=status.HTTP_404_NOT_FOUND)
         
         
        #decrementer ticket repas  
        if (int(heure)>=13) and (int(heure)<=15) or (int(heure)>=18 and int(heure)<=22):
            try:
                ticketRepas =  Ticket_Repas.objects.get(etudiant=etudiant)
                if ticketRepas.nbre_tickets_repas > 0:
                    etudiant.decrementer_ticket_repas()
                    return Response({"message": "Décrémentation réussie","code_permenant": ticketRepas.etudiant.identifiant})
                else:
                    return Response({"error": "Pas de tickets repas pour cet(te) étudiant(e)"}, status=status.HTTP_404_NOT_FOUND)
            except Ticket_Repas.DoesNotExist:
                return Response({'error': 'Pas de tickets repas pour cet(te) etudiant(e)'},
                    status=status.HTTP_404_NOT_FOUND)
            
        # Sérialiser les détails de l'étudiant
        serializer = self.get_serializer(etudiant)
        # Retourner les détails de l'étudiant dans la réponse
        return Response(serializer.data)
    
    
                        
    
    
                        
    # def partial_update(self, request,cp=None):
    #      etudiant = self.get_queryset().get(code_permenant=cp)
    #      etudiant.decrementer_ticket_repas();
        
    #      serializer = EtudiantSerializer(etudiant)
    #      return Response(serializer.data)
    
    
    

        
    

