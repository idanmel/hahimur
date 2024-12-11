# Generated by Django 5.1.2 on 2024-12-11 15:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tournaments', '0025_remove_grouprow_position'),
    ]

    operations = [
        migrations.AddField(
            model_name='grouprow',
            name='position',
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='match',
            name='away_score',
            field=models.PositiveSmallIntegerField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='match',
            name='home_score',
            field=models.PositiveSmallIntegerField(blank=True, default=None, null=True),
        ),
    ]
