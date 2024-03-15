from django.db import models

from Admin.models import User

# Create your models here.





class Personnel(User): 
    photo = models.ImageField(upload_to='personnel/', null=True, blank=True)
    date=models.DateField(auto_now_add=True)
    
    
    
    
    
    def __str__(self):
          if self.first_name is not None and self.last_name is not None:
            return f"{self.first_name} {self.last_name}"
          elif self.last_name is None:
            return self.first_name