from rest_framework.serializers import ModelSerializer,SerializerMethodField

from Etudiants.models import Etudiant
from Tickets.serializers import DejSerializer, RepaSerializer





class EtudiantSerializer(ModelSerializer):
   #tickets = RepaSerializer(many=True, read_only=True)
   tickets_repas = SerializerMethodField()
   tickets_dej = SerializerMethodField()
   class Meta:
        model = Etudiant
        fields = ['id','identifiant','first_name','last_name','tickets_repas','tickets_dej']
        

   def get_tickets_repas(self, instance):
        queryset = instance.tickets_repas.all()
        serializer = RepaSerializer(queryset, many=True)
        return serializer.data
   
   def get_tickets_dej(self, instance):
        queryset = instance.tickets_dej.all()
        serializer = DejSerializer(queryset, many=True)
        return serializer.data