# Generated by Django 3.2.5 on 2021-08-22 15:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0018_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='price',
            name='desc',
            field=models.CharField(default='', max_length=50),
        ),
    ]
