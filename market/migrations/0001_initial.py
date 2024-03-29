# Generated by Django 3.2.5 on 2021-08-05 12:12

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Weapon',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.FloatField()),
                ('weaponId', models.CharField(max_length=100)),
                ('weaponStars', models.IntegerField()),
                ('weaponElement', models.CharField(max_length=100)),
                ('stat1Element', models.CharField(max_length=100)),
                ('stat1Value', models.IntegerField()),
                ('stat2Element', models.CharField(blank=True, default='', max_length=100)),
                ('stat2Value', models.IntegerField(blank=True, default=0)),
                ('stat3Element', models.CharField(blank=True, default='', max_length=100)),
                ('stat3Value', models.IntegerField(blank=True, default=0)),
            ],
        ),
    ]
