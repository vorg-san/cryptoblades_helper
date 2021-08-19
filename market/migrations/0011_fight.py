# Generated by Django 3.2.5 on 2021-08-15 13:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0010_auto_20210813_1626'),
    ]

    operations = [
        migrations.CreateModel(
            name='Fight',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.CharField(max_length=200)),
                ('character', models.CharField(max_length=100)),
                ('xp', models.IntegerField()),
                ('skill_earned', models.FloatField()),
                ('bnb_cost', models.FloatField()),
                ('skill_dollar_price', models.FloatField()),
                ('bnb_dollar_price', models.FloatField()),
            ],
        ),
    ]
