# Generated by Django 5.1.1 on 2024-10-23 22:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('albums', '0002_remove_album_country_remove_album_released_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='album',
            name='length',
            field=models.IntegerField(),
        ),
    ]
