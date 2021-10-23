# Generated by Django 3.2.5 on 2021-10-12 23:03

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('cmc', '0003_auto_20211012_1509'),
    ]

    operations = [
        migrations.CreateModel(
            name='Pull',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(blank=True, default=django.utils.timezone.now)),
            ],
        ),
        migrations.AddField(
            model_name='crypto',
            name='link',
            field=models.CharField(default='', max_length=300),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='data',
            name='pull',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to='cmc.pull'),
            preserve_default=False,
        ),
    ]
