# Generated by Django 3.2.5 on 2021-08-13 19:26

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0009_alter_weapon_options'),
    ]

    operations = [
        migrations.CreateModel(
            name='Character',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('charId', models.CharField(max_length=100)),
                ('seller', models.CharField(max_length=200)),
                ('price', models.FloatField()),
                ('xp', models.IntegerField()),
                ('level', models.IntegerField()),
                ('power', models.IntegerField()),
                ('element', models.CharField(max_length=100)),
                ('powerPerPrice', models.FloatField()),
                ('updated', models.DateTimeField(blank=True, default=django.utils.timezone.now)),
            ],
            options={
                'ordering': ['-powerPerPrice'],
            },
        ),
        migrations.RenameField(
            model_name='weapon',
            old_name='sellerAddress',
            new_name='seller',
        ),
    ]
