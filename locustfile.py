import re
import string
from locust import HttpUser, TaskSet, task, between
import random




class ComportementEtudiant(TaskSet):
    # """Classe de base pour le comportement de l'utilisateur."""
    # def on_start(self):
    #     # Obtenir le jeton CSRF
    #     response = self.client.get("/")
    #     csrf_token = re.search(r'name="csrfmiddlewaretoken" value="(.+?)"', response.text).group(1)
    #     self.client.headers.update({'X-CSRFToken': csrf_token})

    # @task
    # def login(self):
    #     self.client.post("/", {
    #         "identifiant": "1502345",
    #         "password": "123",
    #         "csrfmiddlewaretoken": self.client.headers['X-CSRFToken']
    #     })
        
        
    @task(3)
    def voir_accueil(self):
        """Simule l'action de visiter la page d'accueil."""
        self.client.get("/accueil/")

    @task(2)
    def voir_transactions(self):
        """Simule l'action de consulter la page des transactions."""
        self.client.get("/transaction/")

    @task(1)
    def voir_profil(self):
        """Simule l'action de consulter le profil étudiant."""
        # Assuming the user ID is between 1 and 1000
        user_id = random.randint(10000, 99999)
        self.client.get(f"/{user_id}/detail_etudiant/")

    # @task(1)
    # def envoyer_ticket(self):
    #     """Simule l'action d'envoyer un ticket."""
    #     self.client.post("/send_ticket/", {
    #         # "cp": f"17{random.randint(10000, 99999)}",
    #         "cp": "1702345",
    #         "nbre_tickets": random.randint(1, 10),
    #         "Typeofticket": random.choice(["dej", "repas"])
    #     })

    @task(1)
    def changer_mot_de_passe(self):
        """Simule l'action de changer le mot de passe."""
        user_id = random.randint(10000, 99999)
        self.client.get(f"/{user_id}/changepassword/")

    @task(1)
    def changer_qr_code(self):
        """Simule l'action de changer le QR code."""
        user_id = random.randint(10000, 99999)
        self.client.get(f"/{user_id}/change_qrcode/")
        
    # @task(1)
    # def get_etudiants(self):
    #     """Simule l'action de consulter la liste des etudiants."""
        
    #     self.client.get("/api/etudiant/4IQJQ_Abdoulaye_Mbaye_28qi1A")
        
    # @task(2)
    # def consommer_ticket(self):
    #     """Simule la consommation de tickets par le personnel."""
    #     typeticket = random.choice(["pdej", "dej", "dinner"])
    #     payload = {
    #         "type_ticket": f"{typeticket}",
    #         "quantity": 1
    #     }
    #     self.client.post(f"/api/consommer/restau_campus1/", data=payload)     
    
    

class UtilisateurSiteWeb(HttpUser):
    """Classe principale pour définir le comportement de l'utilisateur dans Locust."""
    tasks = [ComportementEtudiant]
    wait_time = between(1, 3)
    host = "http://192.168.1.8:8000"