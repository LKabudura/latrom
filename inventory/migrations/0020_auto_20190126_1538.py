# Generated by Django 2.1.4 on 2019-01-26 13:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0019_auto_20190126_1537'),
    ]

    operations = [
        migrations.AlterField(
            model_name='consumable',
            name='unit_purchase_price',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=9),
        ),
        migrations.AlterField(
            model_name='equipment',
            name='unit_purchase_price',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=9),
        ),
        migrations.AlterField(
            model_name='product',
            name='unit_purchase_price',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=9),
        ),
        migrations.AlterField(
            model_name='rawmaterial',
            name='unit_purchase_price',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=9),
        ),
    ]