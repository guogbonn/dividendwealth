# Generated by Django 2.2.5 on 2019-12-23 03:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0065_dividendwealthmembership_subscription'),
    ]

    operations = [
        migrations.AddField(
            model_name='dividendwealthsubscription',
            name='sub_date',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
