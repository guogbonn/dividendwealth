# Generated by Django 2.2.5 on 2019-12-30 04:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0069_user_profile_stripe_connected_account_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user_profile',
            name='stripe_connected_account_id',
        ),
        migrations.CreateModel(
            name='DividendWealthConnectedAccount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stripe_connected_account_id', models.CharField(blank=True, max_length=30, null=True)),
                ('user_profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.User_Profile')),
            ],
        ),
    ]
