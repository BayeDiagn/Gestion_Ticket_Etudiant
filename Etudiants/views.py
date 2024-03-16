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
    
    

class MyPasswordResetDoneView(PasswordResetDoneView):
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
        
        
        heure = datetime.datetime.now().hour
        
        
        #decrementer ticket dej
        if (heure)>=6 and int(heure)<=11:
            try:
                ticketDej =  Ticket_Dej.objects.get(etudiant=etudiant)
                if ticketDej.nbre_tickets_dej > 0:
                    etudiant.decrementer_ticket_dej()
                    return Response({"message": "Decrementation reussie!!","code_permenant": ticketDej.etudiant.identifiant})
                else:
                    return Response({"error": "Aucun ticket petit-dejeuner!!"}, status=status.HTTP_404_NOT_FOUND)
            except Ticket_Dej.DoesNotExist:
                return Response({'error': 'Aucun ticket petit-dejeuner!!'},
                    status=status.HTTP_404_NOT_FOUND)
        
        
        #decrementer ticket repas  
        elif (heure)>=12 and (heure)<=15 or (heure)>=18 and int(heure)<=23:
                try:
                    ticketRepas =  Ticket_Repas.objects.get(etudiant=etudiant)
                    if ticketRepas.nbre_tickets_repas > 0:
                        etudiant.decrementer_ticket_repas()
                        return Response({"message": "Decrementation reussie!!","code_permenant": ticketRepas.etudiant.identifiant})
                    else:
                        return Response({"error": "Aucun ticket dejeuner!!"}, status=status.HTTP_404_NOT_FOUND)
                except Ticket_Repas.DoesNotExist:
                    return Response({"error": "Aucun ticket dejeuner!!"},
                    status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"error": "Hors delai!!"}, status=status.HTTP_404_NOT_FOUND)
         
            
        # Sérialiser les détails de l'étudiant
        serializer = self.get_serializer(etudiant)
        # Retourner les détails de l'étudiant dans la réponse
        return Response(serializer.data)
    
    
                        
    
    
                        
    # def partial_update(self, request,cp=None):
    #      etudiant = self.get_queryset().get(code_permenant=cp)
    #      etudiant.decrementer_ticket_repas();
        
    #      serializer = EtudiantSerializer(etudiant)
    #      return Response(serializer.data)
    
    
    

        
    

