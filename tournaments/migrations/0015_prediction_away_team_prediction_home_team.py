# Generated by Django 5.1.2 on 2024-11-10 14:49

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tournaments', '0014_rename_friendscore_friendresult'),
    ]

    operations = [
        migrations.AddField(
            model_name='prediction',
            name='away_team',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='away_team', to='tournaments.team'),
        ),
        migrations.AddField(
            model_name='prediction',
            name='home_team',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='home_team', to='tournaments.team'),
        ),
    ]
