# Generated by Django 5.1.2 on 2024-11-18 09:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tournaments', '0026_remove_match_away_team_remove_match_home_team_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='match',
            options={'ordering': ['-start_time', '-number']},
        ),
        migrations.AlterField(
            model_name='match',
            name='number',
            field=models.PositiveSmallIntegerField(),
        ),
    ]
