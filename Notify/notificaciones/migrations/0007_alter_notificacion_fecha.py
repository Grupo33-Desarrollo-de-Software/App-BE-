# Generated by Django 5.1.1 on 2025-03-04 21:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notificaciones', '0006_alter_notificacion_fecha'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notificacion',
            name='fecha',
            field=models.DateField(auto_now_add=True),
        ),
    ]
