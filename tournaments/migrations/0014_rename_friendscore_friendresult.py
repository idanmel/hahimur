# Generated by Django 5.1.2 on 2024-11-07 06:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tournaments', '0013_rule_advanced_position'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='FriendScore',
            new_name='FriendResult',
        ),
    ]
