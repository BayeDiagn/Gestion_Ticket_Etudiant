# Generated by Django 3.2.6 on 2024-04-07 11:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Etudiants', '0005_alter_transaction_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='date',
            field=models.DateField(auto_now_add=True),
        ),
    ]