# Generated by Django 5.1.5 on 2025-01-25 05:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('landingpage', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='category',
            field=models.CharField(blank=True, max_length=50),
        ),
    ]
