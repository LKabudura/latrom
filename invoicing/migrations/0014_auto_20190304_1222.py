# Generated by Django 2.1.4 on 2019-03-04 10:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('invoicing', '0013_auto_20190201_1959'),
    ]

    operations = [
        migrations.CreateModel(
            name='CreditNoteLine',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.FloatField()),
            ],
        ),
        migrations.RemoveField(
            model_name='salesinvoiceline',
            name='returned_quantity',
        ),
        migrations.AddField(
            model_name='creditnoteline',
            name='line',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='invoicing.SalesInvoiceLine'),
        ),
        migrations.AddField(
            model_name='creditnoteline',
            name='note',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='invoicing.CreditNote'),
        ),
    ]