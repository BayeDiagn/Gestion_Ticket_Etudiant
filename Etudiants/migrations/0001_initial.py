# Generated by Django 3.2.6 on 2024-03-14 07:22

import Etudiants.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('Admin', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Etudiant',
            fields=[
                ('user_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='Admin.user')),
                ('montant', models.FloatField(blank=True, default=0, max_length=200)),
                ('code_qr', models.ImageField(blank=True, upload_to=Etudiants.models.upload_photo_qr)),
                ('date', models.DateField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            bases=('Admin.user',),
        ),
    ]