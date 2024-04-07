# Generated by Django 3.2.6 on 2024-04-02 10:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Personnels', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='personnel',
            old_name='nbre_tickets_consommer',
            new_name='nbre_tickets_dej_consommer',
        ),
        migrations.AddField(
            model_name='personnel',
            name='nbre_tickets_dinner_consommer',
            field=models.FloatField(blank=True, default=0.0, null=True),
        ),
        migrations.AddField(
            model_name='personnel',
            name='nbre_tickets_pdej_consommer',
            field=models.FloatField(blank=True, default=0.0, null=True),
        ),
    ]