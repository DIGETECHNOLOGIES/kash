# Generated by Django 5.1.7 on 2025-03-14 20:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0010_order_payment_id_alter_order_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='shop',
            name='image',
            field=models.ImageField(null=True, upload_to='shop/'),
        ),
        migrations.AlterField(
            model_name='shop',
            name='owner_image',
            field=models.ImageField(null=True, upload_to='shop_owners/'),
        ),
    ]
