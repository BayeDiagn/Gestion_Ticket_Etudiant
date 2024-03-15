from django.db import models

from Etudiants.models import Etudiant






class Ticket_Repas(models.Model):
    nbre_tickets_repas = models.FloatField(null=True, max_length=65,default=0.0,blank=True)
    etudiant = models.ForeignKey(Etudiant,related_name="tickets_repas",on_delete=models.CASCADE)


    def __str__(self) :
        return f"{self.etudiant.first_name}_{self.etudiant.last_name} (Tickets Repas)"




class Ticket_Dej(models.Model):
    nbre_tickets_dej = models.FloatField(null=True, max_length=65,default=0.0,blank=True)
    etudiant = models.ForeignKey(Etudiant,related_name="tickets_dej",on_delete=models.CASCADE)
    
     
    
    def __str__(self) :
        return f"{self.etudiant.first_name}_{self.etudiant.last_name} (Tickets Dejeuner)"