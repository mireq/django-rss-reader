# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-09-19 16:49
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='category name')),
                ('order', models.PositiveIntegerField(db_index=True, default=0, verbose_name='order')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='user')),
            ],
            options={
                'verbose_name': 'Category',
                'verbose_name_plural': 'Categories',
                'ordering': ('order',),
            },
        ),
        migrations.CreateModel(
            name='Entry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('guid', models.CharField(max_length=1000, verbose_name='unique identifier')),
                ('link', models.CharField(blank=True, max_length=1000, verbose_name='link to article')),
                ('title', models.CharField(blank=True, max_length=1000, verbose_name='news title')),
                ('summary', models.TextField(blank=True, verbose_name='summary')),
                ('content', models.TextField(blank=True, verbose_name='content')),
                ('created', models.DateTimeField(blank=True, db_index=True, null=True, verbose_name='created date')),
                ('updated', models.DateTimeField(blank=True, null=True, verbose_name='updated date')),
                ('author_name', models.CharField(blank=True, max_length=200, verbose_name='name of author')),
            ],
            options={
                'verbose_name': 'News entry',
                'verbose_name_plural': 'News entries',
            },
        ),
        migrations.CreateModel(
            name='Feed',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(editable=False, verbose_name='created')),
                ('updated', models.DateTimeField(editable=False, verbose_name='updated')),
                ('title', models.CharField(max_length=200, verbose_name='feed title')),
                ('description', models.TextField(blank=True, verbose_name='feed description')),
                ('xml_url', models.URLField(unique=True, verbose_name='URL of feed')),
                ('html_url', models.URLField(blank=True, verbose_name='URL of html page')),
                ('language', models.CharField(blank=True, max_length=20, verbose_name='language')),
                ('last_build_date', models.DateTimeField(blank=True, null=True, verbose_name='last build date')),
                ('last_update_date', models.DateTimeField(blank=True, null=True, verbose_name='last update date')),
                ('update_status', models.CharField(blank=True, choices=[('', 'Not updated'), ('u', 'Updated'), ('e', 'Update error')], max_length=1, verbose_name='update status')),
                ('update_error', models.TextField(blank=True, verbose_name='update error')),
            ],
            options={
                'verbose_name': 'Feed',
                'verbose_name_plural': 'Feeds',
            },
        ),
        migrations.CreateModel(
            name='UserEntryStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_unread', models.BooleanField(db_index=True, default=False, verbose_name='news is unread')),
                ('is_favorite', models.BooleanField(db_index=True, default=False, verbose_name='news is favorite')),
                ('entry', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='status', to='feeds.Entry', verbose_name='news item')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='user')),
            ],
            options={
                'verbose_name': 'News entry status for user',
                'verbose_name_plural': 'News entry statuses for user',
            },
        ),
        migrations.CreateModel(
            name='UserFeed',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='feed name')),
                ('order', models.PositiveIntegerField(db_index=True, default=0, verbose_name='order')),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='feeds.Category', verbose_name='category')),
                ('feed', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='feeds.Feed', verbose_name='feed')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='user')),
            ],
            options={
                'verbose_name': ('Feed for user',),
                'verbose_name_plural': 'Feeds for user',
                'ordering': ('order',),
            },
        ),
        migrations.AddField(
            model_name='entry',
            name='feed',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='feeds.Feed', verbose_name='feed'),
        ),
        migrations.AlterUniqueTogether(
            name='userfeed',
            unique_together=set([('user', 'feed')]),
        ),
        migrations.AlterUniqueTogether(
            name='userentrystatus',
            unique_together=set([('user', 'entry')]),
        ),
        migrations.AlterUniqueTogether(
            name='entry',
            unique_together=set([('feed', 'guid')]),
        ),
    ]
