from rest_framework.serializers import ModelSerializer

from .models import Personnel,TicketConsommer





class PersonnelSerializer(ModelSerializer):
    
   class Meta:
        model = Personnel
        fields = ['id','identifiant','first_name','last_name']
        

class TicketConsommerSerializer(ModelSerializer):
    
   class Meta:
        model = TicketConsommer
        fields = ['id','type_ticket','quantity']