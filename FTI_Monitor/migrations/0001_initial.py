# Generated by Django 4.1.7 on 2023-04-13 08:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Tabless',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(default='name', max_length=500, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Rows',
            fields=[
                ('id', models.IntegerField(auto_created=True, primary_key=True, serialize=False)),
                ('Teilindikator', models.CharField(blank=True, max_length=500, null=True)),
                ('Datenquelle', models.CharField(blank=True, max_length=500, null=True)),
                ('Code', models.CharField(blank=True, max_length=500, null=True)),
                ('Datum', models.DateField(blank=True, null=True)),
                ('Status', models.CharField(default='Active', max_length=500)),
                ('Wert', models.CharField(blank=True, max_length=500, null=True)),
                ('Top3', models.IntegerField(blank=True, null=True)),
                ('EUDurchschnitt', models.IntegerField(blank=True, null=True)),
                ('Tables', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='FTI_Monitor.tabless')),
            ],
        ),
    ]
