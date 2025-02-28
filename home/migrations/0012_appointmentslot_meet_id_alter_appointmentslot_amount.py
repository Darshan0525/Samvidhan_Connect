# Generated by Django 5.1.3 on 2024-12-25 06:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0011_remove_bookedappointment_booked_at_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointmentslot',
            name='meet_id',
            field=models.PositiveIntegerField(blank=True, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='appointmentslot',
            name='amount',
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
    ]
