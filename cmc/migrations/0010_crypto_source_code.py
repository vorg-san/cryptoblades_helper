# Generated by Django 3.2.5 on 2021-10-17 18:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cmc', '0009_cryptoexchange_pair'),
    ]

    operations = [
        migrations.AddField(
            model_name='crypto',
            name='source_code',
            field=models.CharField(blank=True, max_length=2000, null=True),
        ),
    ]
