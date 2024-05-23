# Etudiants/models.py
import os
import random
import string
from django.conf import settings
from django.db import models

import qrcode
from io import BytesIO
from django.core.files import File
from PIL import Image, ImageDraw

from Admin.models import User








    
    
    
    
def upload_photo_qr(instance, filename):
    user_folder = f"{instance.identifiant}_{instance.first_name}_{instance.last_name}"
    return os.path.join("Code_QR", user_folder, filename)



class Etudiant (User):
    #montant = models.FloatField(max_length=200,default=0,blank=True)
    code_qr_content = models.CharField(max_length=200,blank=True,unique=True)
    code_qr_img = models.ImageField(upload_to=upload_photo_qr,blank=True)
    date_updated=models.DateTimeField(auto_now=True)
    
    
    
    #Décrementer ticket repas
    def decrementer_ticket_repas(self,nbre_ticket):
        from Tickets.models import Ticket_Repas
        tickets_repas_etudiant = Ticket_Repas.objects.filter(etudiant=self)
        nbre_tickets_repas_max = max(ticket.nbre_tickets_repas for ticket in tickets_repas_etudiant)
        tickets_repas_etudiant = Ticket_Repas.objects.filter(etudiant=self, nbre_tickets_repas=nbre_tickets_repas_max).last()
        tickets_repas_etudiant.nbre_tickets_repas -= nbre_ticket
        tickets_repas_etudiant.save()
          
     
     
            
    #décrementer ticket dej         
    def decrementer_ticket_dej(self,nbre_ticket):
        from Tickets.models import Ticket_Dej
        tickets_dej_etudiant = Ticket_Dej.objects.filter(etudiant=self)
        nbre_tickets_dej_max = max(ticket.nbre_tickets_dej for ticket in tickets_dej_etudiant)
        tickets_dej_etudiant = Ticket_Dej.objects.filter(etudiant=self, nbre_tickets_dej=nbre_tickets_dej_max).last()
        # if ticket_dej.nbre_tickets_dej > 0:
        tickets_dej_etudiant.nbre_tickets_dej -= nbre_ticket
        tickets_dej_etudiant.save()

     
            
    
    #Incrementer ticket repas
    # def incrementer_ticket_repas(self,nbre_tickets):
    #     from Tickets.models import Ticket_Repas
    #     ticket_repas = Ticket_Repas.objects.filter(etudiant=self).last() 
    #     if nbre_tickets > 0 and ticket_repas:
    #         ticket_repas.nbre_tickets_repas += nbre_tickets
    #         ticket_repas.save()
    
    
    
    #Incrementer ticket dej        
    # def incrementer_ticket_dej(self,nbre_tickets):
    #     from Tickets.models import Ticket_Dej
    #     ticket_dej = Ticket_Dej.objects.filter(etudiant=self).last() 
    #     if nbre_tickets > 0:
    #         ticket_dej.nbre_tickets_dej += nbre_tickets
    #         ticket_dej.save()
            
    
    
    
    def __str__(self) :
        return f"{self.first_name} {self.last_name} {self.id}"
    
    
    #redefinition de le methode save()
    def save(self, *args, **kwargs):
        
        # Supprimer l'ancienne image QR si elle existe
        if self.pk and self.code_qr_img:
            self.code_qr_img.delete(save=False)
            
        else:
            super().save(*args, **kwargs)

        chaine_unique1 = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
        chaine_unique2 = ''.join(random.choices(string.ascii_letters + string.digits, k=5))
        self.code_qr_content = f"{chaine_unique1}_{self.first_name}_{self.last_name}_{self.pk}{chaine_unique2}"
            
        qr = qrcode.QRCode(
            version=4,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(self.code_qr_content)
        qr.make(fit=True)
            
        # Générer l'image du code QR
        img = qr.make_image(fill_color="black", back_color="white")
            
        # logo_path = settings.STATIC_ROOT / 'images/uadbqrcode.png'
        # logo = Image.open(logo_path)

            
        # logo_size = 100
        # logo = logo.resize((logo_size, logo_size))

        # pos = (
        #     (img.size[0] - logo_size) // 2,
        #     (img.size[1] - logo_size) // 2  
        # )
        # img.paste(logo, pos, mask=logo)
            
        buffer = BytesIO()
        img.save(buffer, format='PNG')    
        fname = f"Qrcode-{self.identifiant}.png"
        self.code_qr_img.save(fname, File(buffer), save=False)
        
        super(Etudiant, self).save(*args, **kwargs)  # Sauvegarder l'instance avec les nouvelles informations

        
        # if not self.tickets_repas.exists():
        #     # S'il n'y en a pas, initialise nbre_tickets_repas à 0
        #     Ticket_Repas.objects.create(etudiant=self, nbre_tickets_repas=0.0)
            
        # if not self.tickets_dej.exists():
        #     # S'il n'y en a pas, initialise nbre_tickets_dej à 0
        #     Ticket_Dej.objects.create(etudiant=self, nbre_tickets_dej=0.0)
            


class Transaction (models.Model):
    description = models.TextField(max_length=250, null = True, blank = True)
    etudiant = models.ForeignKey(Etudiant,related_name="description",on_delete=models.CASCADE)
    tickets_pdej = models.PositiveIntegerField(default=0, null=True, blank=True)
    tickets_dej = models.PositiveIntegerField(default=0, null=True, blank=True)
    date_created=models.DateTimeField(auto_now_add=True)
    #date=models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.etudiant.first_name}_{self.etudiant.last_name} (Transactions)"