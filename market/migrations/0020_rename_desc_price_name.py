# Generated by Django 3.2.5 on 2021-08-22 15:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0019_price_desc'),
    ]

    operations = [
        migrations.RenameField(
            model_name='price',
            old_name='desc',
            new_name='name',
        ),
    ]
