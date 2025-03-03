# Generated by Django 2.2.5 on 2020-01-06 22:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0075_groupmetrics'),
    ]

    operations = [
        migrations.CreateModel(
            name='GroupSubscription',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subscription', models.BooleanField(default=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('price', models.IntegerField(blank=True, null=True)),
                ('next_payment', models.DateTimeField(null=True)),
                ('connected_account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.User_Profile')),
                ('group_member', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.GroupMember')),
            ],
        ),
        migrations.CreateModel(
            name='GroupPayment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.IntegerField(blank=True, null=True)),
                ('charge_date', models.DateTimeField(auto_now_add=True, null=True)),
                ('description', models.CharField(blank=True, max_length=500, null=True)),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.GenGroup')),
                ('person_paying', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.User_Profile')),
                ('person_receiving', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reciver', to='core.User_Profile')),
            ],
        ),
    ]
