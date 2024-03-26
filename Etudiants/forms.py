from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import Etudiant





class EtudiantCreationForm(UserCreationForm):
    class Meta:
        model = Etudiant
        fields = ['first_name','last_name','identifiant','email','password1','password2']




class SendTicketForm(forms.ModelForm):
    nbre_tickets = forms.FloatField(required=True, initial=0.0)
    cp=forms.CharField(max_length=200)
    TYPE_TICKETS = [
        ('dej', 'Ticket Petit-Déjeuner'),
        ('repas', 'Ticket Déjeuner'),
    ]
    Typeofticket = forms.ChoiceField(choices=TYPE_TICKETS, required=True)
    class Meta:
        model = Etudiant
        fields = ['cp','nbre_tickets','Typeofticket']