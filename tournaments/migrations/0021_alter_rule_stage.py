# Generated by Django 5.1.2 on 2024-11-11 07:15

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tournaments', '0020_alter_friendresult_prediction'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rule',
            name='stage',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='tournaments.stage'),
        ),
    ]