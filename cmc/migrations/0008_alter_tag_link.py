# Generated by Django 3.2.5 on 2021-10-16 00:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cmc', '0007_tag_link'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tag',
            name='link',
            field=models.CharField(blank=True, max_length=3000, null=True),
        ),
    ]
