# Generated by Django 3.2.5 on 2021-08-07 20:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0002_weapon_updated'),
    ]

    operations = [
        migrations.AddField(
            model_name='weapon',
            name='power',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
    ]
