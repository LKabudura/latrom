# Generated by Django 2.1.1 on 2018-10-08 09:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0028_auto_20181008_1040'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inventorycheck',
            name='adjusted_by',
            field=models.ForeignKey(limit_choices_to=models.Q(user__isnull=False), on_delete=None, to='employees.Employee'),
        ),
        migrations.AlterField(
            model_name='inventorycontroller',
            name='employee',
            field=models.ForeignKey(limit_choices_to=models.Q(user__isnull=False), on_delete=None, to='employees.Employee'),
        ),
        migrations.AlterField(
            model_name='inventoryscrappingrecord',
            name='controller',
            field=models.ForeignKey(limit_choices_to=models.Q(user__isnull=False), on_delete=None, to='employees.Employee'),
        ),
        migrations.AlterField(
            model_name='stockreceipt',
            name='received_by',
            field=models.ForeignKey(default=1, limit_choices_to=models.Q(user__isnull=False), on_delete=None, to='employees.Employee'),
        ),
        migrations.AlterField(
            model_name='transferorder',
            name='issuing_inventory_controller',
            field=models.ForeignKey(limit_choices_to=models.Q(user__isnull=False), null=True, on_delete=None, related_name='issuing_inventory_controller', to='employees.Employee'),
        ),
        migrations.AlterField(
            model_name='transferorder',
            name='receiving_inventory_controller',
            field=models.ForeignKey(limit_choices_to=models.Q(user__isnull=False), null=True, on_delete=None, to='employees.Employee'),
        ),
        migrations.AlterField(
            model_name='warehouse',
            name='inventory_controller',
            field=models.ForeignKey(blank=True, limit_choices_to=models.Q(user__isnull=False), null=True, on_delete=None, to='employees.Employee'),
        ),
    ]
