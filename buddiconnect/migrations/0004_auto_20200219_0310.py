# Generated by Django 2.2.6 on 2020-02-19 03:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('buddiconnect', '0003_auto_20200217_2138'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='seeker',
            field=models.BooleanField(blank=True, default=True),
        ),
    ]
