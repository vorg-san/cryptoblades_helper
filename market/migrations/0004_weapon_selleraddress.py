# Generated by Django 3.2.5 on 2021-08-07 22:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0003_weapon_power'),
    ]

    operations = [
        migrations.AddField(
            model_name='weapon',
            name='sellerAddress',
            field=models.CharField(default=2, max_length=200),
            preserve_default=False,
        ),
    ]
