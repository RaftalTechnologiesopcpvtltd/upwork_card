# Generated by Django 5.1.5 on 2025-02-25 10:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('landingpage', '0015_rename_est_arrival_product_estimated_arrival_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='selling_type',
            field=models.CharField(default='', max_length=10, null=True),
        ),
    ]
