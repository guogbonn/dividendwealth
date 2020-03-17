# Generated by Django 2.2.5 on 2019-10-31 02:57

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0028_auto_20191029_2059'),
    ]

    operations = [
        migrations.CreateModel(
            name='Archive',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.AddField(
            model_name='post',
            name='hidden',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='post',
            name='reported',
            field=models.IntegerField(default=0),
        ),
        migrations.CreateModel(
            name='PostArchive',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_included', models.DateField(auto_now_add=True, null=True)),
                ('archive', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Archive')),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Post')),
            ],
        ),
        migrations.CreateModel(
            name='CommentsArchive',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_included', models.DateField(auto_now_add=True, null=True)),
                ('archive', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Archive')),
                ('comment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Comments')),
            ],
        ),
        migrations.CreateModel(
            name='CommentReplyArchive',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_included', models.DateField(auto_now_add=True, null=True)),
                ('archive', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Archive')),
                ('reply', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.CommentReply')),
            ],
        ),
        migrations.AddField(
            model_name='archive',
            name='commentreply',
            field=models.ManyToManyField(blank=True, through='core.CommentReplyArchive', to='core.CommentReply'),
        ),
        migrations.AddField(
            model_name='archive',
            name='comments',
            field=models.ManyToManyField(blank=True, through='core.CommentsArchive', to='core.Comments'),
        ),
        migrations.AddField(
            model_name='archive',
            name='posts',
            field=models.ManyToManyField(blank=True, through='core.PostArchive', to='core.Post'),
        ),
        migrations.AddField(
            model_name='archive',
            name='userprofile',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
