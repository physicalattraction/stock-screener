# Generated by Django 3.1.2 on 2020-10-18 16:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('currency', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Stock',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('symbol', models.CharField(help_text='Symbol to look up the stock on Yahoo finance', max_length=16, unique=True)),
                ('ticker', models.CharField(blank=True, max_length=32, null=True)),
                ('name', models.CharField(max_length=64)),
                ('currency', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='currency.currency')),
            ],
            options={
                'ordering': ('symbol',),
            },
        ),
        migrations.CreateModel(
            name='StockPrice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('open', models.DecimalField(decimal_places=4, max_digits=10)),
                ('close', models.DecimalField(blank=True, decimal_places=4, max_digits=10, null=True)),
                ('high', models.DecimalField(blank=True, decimal_places=4, max_digits=10, null=True)),
                ('low', models.DecimalField(blank=True, decimal_places=4, max_digits=10, null=True)),
                ('stock', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='prices', to='stock.stock')),
            ],
            options={
                'ordering': ('stock', 'date'),
            },
        ),
    ]
