# Generated by Django 3.2.3 on 2021-06-02 07:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('btForum', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='torrent',
            name='count',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='user',
            name='totDown',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='user',
            name='totUp',
            field=models.FloatField(default=0),
        ),
    ]