# Generated by Django 5.1.6 on 2025-03-04 12:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Proyecto_SENA', '0004_pedido_comprobante_pago'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historialpedidos',
            name='compra_total',
            field=models.DecimalField(decimal_places=0, max_digits=10),
        ),
    ]
