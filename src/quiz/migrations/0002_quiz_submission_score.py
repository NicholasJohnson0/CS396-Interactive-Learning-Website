# Generated by Django 4.2.5 on 2023-10-03 04:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='quiz_submission',
            name='score',
            field=models.IntegerField(default=0),
        ),
    ]
