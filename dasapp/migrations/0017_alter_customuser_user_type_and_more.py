# Generated by Django 4.2.11 on 2025-03-24 16:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dasapp', '0016_alter_customuser_user_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='user_type',
            field=models.CharField(choices=[(1, 'admin'), ('3', 'lab_worker'), ('4', 'pharmacist'), (2, 'doc')], default=1, max_length=50),
        ),
        migrations.AlterField(
            model_name='prescription',
            name='additional_notes',
            field=models.TextField(blank=True),
        ),
    ]
