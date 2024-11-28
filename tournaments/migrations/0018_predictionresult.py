# Generated by Django 5.1.2 on 2024-11-27 19:48

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tournaments', '0017_delete_predictionresult'),
    ]

    operations = [
        migrations.CreateModel(
            name='PredictionResult',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('points', models.PositiveSmallIntegerField(default=0)),
                ('result', models.CharField(choices=[('WO', 'Wrong'), ('HI', 'Hit'), ('BU', 'Bullseye'), ('NO', 'Not Participated')], default=None, max_length=2, null=True)),
                ('prediction', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='tournaments.prediction')),
            ],
        ),
    ]