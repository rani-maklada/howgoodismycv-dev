# Generated by Django 4.1.13 on 2024-04-02 09:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0005_analysisresult_googleimage'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='analysisresult',
            name='googleimage',
        ),
        migrations.AddField(
            model_name='analysisresult',
            name='googleimages',
            field=models.TextField(default='[]'),
        ),
    ]
