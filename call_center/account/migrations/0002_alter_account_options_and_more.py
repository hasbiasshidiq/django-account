# Generated by Django 5.0.6 on 2024-05-23 17:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='account',
            options={'ordering': ['created_at']},
        ),
        migrations.RenameField(
            model_name='account',
            old_name='created',
            new_name='created_at',
        ),
    ]