from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager









class UserManager(BaseUserManager):
     
     def create_user(self, identifiant, password=None, **extra_fields):
            if not identifiant: 
               raise ValueError('Votre identifiant est obligatoire.')

            #email = self.normalize_email(email)
            user = self.model(identifiant=identifiant, **extra_fields)
            user.set_password(password)
            user.save(using=self._db)
            return user
    
     def create_superuser(self, identifiant, password=None, **extra_fields):
        
        # Crée le superuser    
        user = self.create_user(identifiant, password, **extra_fields)  
        user.is_staff = True
        user.is_superuser = True
        user.save()
        
        return user
    
    
    
    
class User(AbstractUser):
    email = models.EmailField(unique=True)
    identifiant=models.CharField(null=True,max_length=200,unique=True)
    is_etudiant = models.BooleanField(default=True)
    is_personnel = models.BooleanField(default=False)
    is_boutiquier = models.BooleanField(default=False)
    failed_login = models.PositiveIntegerField(default=0)
    account_locked_until = models.DateTimeField(null=True, blank=True)
    
    
    username = None
    
    USERNAME_FIELD = 'identifiant'  
    REQUIRED_FIELDS = ['first_name','last_name','email']

    
    objects = UserManager()
    
    
    def __str__(self) :
        return f"{self.first_name} {self.last_name}"