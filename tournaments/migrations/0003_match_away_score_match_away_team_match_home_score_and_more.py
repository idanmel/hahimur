# Generated by Django 5.1.2 on 2024-11-21 07:08

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tournaments', '0002_match_match_stage_number_uniq'),
    ]

    operations = [
        migrations.AddField(
            model_name='match',
            name='away_score',
            field=models.PositiveSmallIntegerField(default=None),
        ),
        migrations.AddField(
            model_name='match',
            name='away_team',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='away', to='tournaments.team'),
        ),
        migrations.AddField(
            model_name='match',
            name='home_score',
            field=models.PositiveSmallIntegerField(default=None),
        ),
        migrations.AddField(
            model_name='match',
            name='home_team',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='home', to='tournaments.team'),
        ),
    ]
