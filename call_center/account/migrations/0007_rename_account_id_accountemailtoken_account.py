# Generated by Django 5.0.6 on 2024-05-25 03:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0006_alter_account_options_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='accountemailtoken',
            old_name='account_id',
            new_name='account',
        ),
    ]
