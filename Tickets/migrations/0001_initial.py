# Generated by Django 5.0.4 on 2024-05-22 23:35

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('Etudiants', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Ticket_Dej',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nbre_tickets_dej', models.PositiveIntegerField(blank=True, default=0, null=True)),
                ('etudiant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tickets_dej', to='Etudiants.etudiant')),
            ],
        ),
        migrations.CreateModel(
            name='Ticket_Repas',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nbre_tickets_repas', models.PositiveIntegerField(blank=True, default=0, null=True)),
                ('etudiant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tickets_repas', to='Etudiants.etudiant')),
            ],
        ),
    ]
