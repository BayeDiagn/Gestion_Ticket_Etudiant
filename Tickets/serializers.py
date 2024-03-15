from rest_framework.serializers import ModelSerializer

from .models import Ticket_Dej,Ticket_Repas





class RepaSerializer(ModelSerializer):
    
   class Meta:
        model = Ticket_Repas
        fields = ['id','nbre_tickets_repas','etudiant']
        

class DejSerializer(ModelSerializer):
    
   class Meta:
        model = Ticket_Dej
        fields = ['id','nbre_tickets_dej','etudiant']