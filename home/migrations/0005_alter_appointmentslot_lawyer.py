# Generated by Django 5.1.4 on 2024-12-21 17:51

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0001_initial'),
        ('home', '0004_appointment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appointmentslot',
            name='lawyer',
            field=models.ForeignKey(limit_choices_to={'role': 'lawyer'}, on_delete=django.db.models.deletion.CASCADE, to='authentication.users'),
        ),
    ]
