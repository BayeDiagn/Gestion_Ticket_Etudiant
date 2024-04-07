from django.db import models

from Admin.models import User

# Create your models here.





class Personnel(User): 
    date=models.DateField(auto_now_add=True)
    
    
    
    
    
    def __str__(self):
          if self.first_name is not None and self.last_name is not None:
            return f"{self.first_name} {self.last_name}"
          elif self.last_name is None:
            return self.first_name
          
          

class TicketConsommer(models.Model):
    TYPE_CHOICES = (
        ('pdej', 'Petit-déjeuner'),
        ('dej', 'Déjeuner'),
        ('dinner', 'Dîner'),
    )
    type_ticket = models.CharField(max_length=10, choices=TYPE_CHOICES)
    quantity = models.PositiveIntegerField(default=0)
    personnel = models.ForeignKey(Personnel, on_delete=models.CASCADE, related_name='tickets')
    date = models.DateField(auto_now_add=True)