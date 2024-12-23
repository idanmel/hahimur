# Generated by Django 5.1.2 on 2024-11-25 09:50

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tournaments', '0008_alter_prediction_result'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='stagepoint',
            options={'ordering': ['stage', '-points', '-friend']},
        ),
        migrations.AlterField(
            model_name='prediction',
            name='result',
            field=models.CharField(choices=[('WO', 'Wrong'), ('HI', 'Hit'), ('BU', 'Bullseye'), ('NO', 'Not Participated')], default=None, max_length=2, null=True),
        ),
        migrations.CreateModel(
            name='TopScorerPoint',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('points', models.PositiveSmallIntegerField(default=0)),
                ('friend', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('match', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tournaments.match')),
            ],
        ),
    ]
