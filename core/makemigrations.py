import datetime

from django.db import migrations


def create_through_relations(apps, schema_editor):
    Group = apps.get_model('core', 'UserProfile')
    Membership = apps.get_model('core', 'StockInfo')
    for user in UserProfile.objects.all():
        for member in UserProfile.stock.all():
            StockInfo(
                stock=member,
                userprofile=group,
            ).save()

class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0005_create_models'),
    ]

    operations = [
        migrations.RunPython(create_through_relations, reverse_code=migrations.RunPython.noop),
    ]
