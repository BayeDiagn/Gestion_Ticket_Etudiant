import os
from django.db import models

import qrcode
from io import BytesIO
from django.core.files import File
#from PIL import Image, ImageDraw

from Admin.models import User








    
    
    
    
def upload_photo_qr(instance, filename):
    user_folder = f"{instance.identifiant}_{instance.first_name}_{instance.last_name}"
    return os.path.join("Code_QR", user_folder, filename)



class Etudiant (User):
    #montant = models.FloatField(max_length=200,default=0,blank=True)
    code_qr = models.ImageField(upload_to=upload_photo_qr,blank=True)
    date=models.DateField(auto_now_add=True)
    
    
    #Décrementer ticket repas
    def decrementer_ticket_repas(self,nbre_ticket):
        from Tickets.models import Ticket_Repas
        ticket_repas = Ticket_Repas.objects.get(etudiant=self) 
        ticket_repas.nbre_tickets_repas -= nbre_ticket
        ticket_repas.save()
            #print(f"Ticket repas décrémenté pour {self.first_name} {self.last_name}, {ticket_repas.nbre_tickets_repas} tickets restants.")
        # else:
        #     print(f"Pas de tickets repas restants pour {self.first_name} {self.last_name}")
     
     
            
    #décrementer ticket dej         
    def decrementer_ticket_dej(self,nbre_ticket):
        from Tickets.models import Ticket_Dej
        ticket_dej = Ticket_Dej.objects.get(etudiant=self) 
        # if ticket_dej.nbre_tickets_dej > 0:
        ticket_dej.nbre_tickets_dej -= nbre_ticket
        ticket_dej.save()
        #     print(f"Ticket dej décrémenté pour {self.first_name} {self.last_name}, {ticket_dej.nbre_tickets_dej} tickets restants.")
        # else:
        #     print(f"Pas de tickets dej restants pour {self.first_name} {self.last_name}")
     
            
    
    #Incrementer ticket repas
    def incrementer_ticket_repas(self,nbre_tickets):
        from Tickets.models import Ticket_Repas
        ticket_repas = Ticket_Repas.objects.get(etudiant=self) 
        if nbre_tickets > 0:
            ticket_repas.nbre_tickets_repas += nbre_tickets
            ticket_repas.save()
    
    
    
    #Incrementer ticket dej        
    def incrementer_ticket_dej(self,nbre_tickets):
        from Tickets.models import Ticket_Dej
        ticket_dej = Ticket_Dej.objects.get(etudiant=self) 
        if nbre_tickets > 0:
            ticket_dej.nbre_tickets_dej += nbre_tickets
            ticket_dej.save()
            
    
    
    
    def __str__(self) :
        return f"{self.first_name} {self.last_name}"
    
    
    #redefinition de le methode save()
    def save(self,*args, **kwargs):
        from Tickets.models import Ticket_Dej, Ticket_Repas
        if not self.pk:
            qr = qrcode.QRCode(
                version=3,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(self.identifiant)
            qr.make(fit=True)

            img = qr.make_image(fill_color="black", back_color="white")
            buffer = BytesIO()
            img.save(buffer, format='PNG')    
            fname = f"Qrcode-{self.identifiant}.png"
            self.code_qr.save(fname,File(buffer),save=False)
            
            super().save(*args, **kwargs)
        
        if not self.tickets_repas.exists():
            # S'il n'y en a pas, initialise nbre_tickets_repas à 0
            Ticket_Repas.objects.create(etudiant=self, nbre_tickets_repas=0.0)
            
        if not self.tickets_dej.exists():
            # S'il n'y en a pas, initialise nbre_tickets_dej à 0
            Ticket_Dej.objects.create(etudiant=self, nbre_tickets_dej=0.0)
            


class Transaction (models.Model):
    description = models.TextField(max_length=250, null = True, blank = True)
    etudiant = models.ForeignKey(Etudiant,related_name="description",on_delete=models.CASCADE)
    date=models.DateTimeField(auto_now_add=True)
    #date=models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.etudiant.first_name}_{self.etudiant.last_name} (Transactions)"