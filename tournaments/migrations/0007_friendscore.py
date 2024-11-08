# Generated by Django 5.1.2 on 2024-11-04 13:06

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tournaments', '0006_match_stage'),
    ]

    operations = [
        migrations.CreateModel(
            name='FriendScore',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.IntegerField()),
                ('prediction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tournaments.prediction')),
            ],
        ),
    ]
