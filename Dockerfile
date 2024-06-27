# Utilise l'image officielle de Python 3.9 comme base
FROM python:3.10.9

# Définit le répertoire de travail à l'intérieur du conteneur
WORKDIR /Gestion_Tickets

# Copie les fichiers requirements.txt et poetry.lock (si vous utilisez Poetry)
COPY requirements.txt requirements.txt

# Installe les dépendances Python
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copie le reste du code de l'application dans le conteneur
COPY . .

# Collecte les fichiers statiques Django
RUN python manage.py collectstatic --no-input

# Expose le port 8000 pour le serveur web
EXPOSE 8000

# Expose le port 8089 pour l'interface web de Locust
# EXPOSE 8089

# Définit la variable d'environnement pour le mode DEBUG de Django
ENV DJANGO_DEBUG=False

# Commande à exécuter lors du démarrage du conteneur
# CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
CMD python manage.py runserver 0.0.0.0:8000