from django.db import models

from Etudiants.models import Etudiant






class Ticket_Repas(models.Model):
    nbre_tickets_repas = models.PositiveIntegerField(default=0, null=True, blank=True)
    etudiant = models.ForeignKey(Etudiant,related_name="tickets_repas",on_delete=models.CASCADE)
    
    def save(self, *args, **kwargs):
        # Vérifie si nbre_tickets_repas est None, si oui, le définit à 0
        if self.nbre_tickets_repas is None:
            self.nbre_tickets_repas = 0.0
        super().save(*args, **kwargs)



    def __str__(self) :
        return f"{self.etudiant.first_name}_{self.etudiant.last_name} (Tickets Repas)"




class Ticket_Dej(models.Model):
    nbre_tickets_dej = models.PositiveIntegerField(default=0, null=True, blank=True)
    etudiant = models.ForeignKey(Etudiant,related_name="tickets_dej",on_delete=models.CASCADE)
    
    def save(self, *args, **kwargs):
        # Vérifie si nbre_tickets_repas est None, si oui, le définit à 0
        if self.nbre_tickets_dej is None:
            self.nbre_tickets_dej = 0.0
        super().save(*args, **kwargs)

    
     
    
    def __str__(self) :
        return f"{self.etudiant.first_name}_{self.etudiant.last_name} (Tickets Dejeuner)"
    
    
    

