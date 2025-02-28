# Generated by Django 5.1.4 on 2024-12-21 16:56

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0001_initial'),
        ('home', '0003_alter_appointmentslot_specialization_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Appointment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_booked', models.BooleanField(default=False)),
                ('slot', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.appointmentslot')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='authentication.users')),
            ],
        ),
    ]
