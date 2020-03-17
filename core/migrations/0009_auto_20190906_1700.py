# Generated by Django 2.2 on 2019-09-07 00:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_auto_20190829_2115'),
    ]

    operations = [
        migrations.CreateModel(
            name='GenGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=500, null=True)),
                ('description', models.CharField(blank=True, max_length=500, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Topic',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=500, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=500, null=True)),
                ('description', models.CharField(blank=True, max_length=500, null=True)),
                ('contents', models.CharField(blank=True, max_length=500, null=True)),
                ('likes', models.IntegerField(default=0)),
                ('viewcount', models.IntegerField(default=0)),
                ('published', models.DateField(blank=True, null=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.User_Profile')),
                ('stocks', models.ManyToManyField(blank=True, to='core.Stocks')),
                ('topic', models.ManyToManyField(blank=True, to='core.Topic')),
            ],
        ),
        migrations.CreateModel(
            name='GroupMember',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stock', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.GenGroup')),
                ('userprofile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.User_Profile')),
            ],
        ),
        migrations.AddField(
            model_name='gengroup',
            name='members',
            field=models.ManyToManyField(blank=True, through='core.GroupMember', to='core.User_Profile'),
        ),
        migrations.CreateModel(
            name='Comments',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('contents', models.CharField(blank=True, max_length=500, null=True)),
                ('likes', models.IntegerField(default=0)),
                ('published', models.DateField(blank=True, null=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.User_Profile')),
                ('post', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='post_comment', to='core.Post')),
                ('stock', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='stock_comment', to='core.Stocks')),
            ],
        ),
    ]
