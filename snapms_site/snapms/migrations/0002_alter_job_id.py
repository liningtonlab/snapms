# Generated by Django 3.2.3 on 2021-05-28 01:49

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('snapms', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='job',
            name='id',
            field=models.CharField(default=uuid.uuid4, editable=False, max_length=32, primary_key=True, serialize=False),
        ),
    ]
