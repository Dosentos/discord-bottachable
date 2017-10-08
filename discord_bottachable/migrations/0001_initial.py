# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-10-07 13:23
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Link',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.CharField(max_length=2048)),
                ('channel_id', models.CharField(max_length=64)),
                ('server_id', models.CharField(max_length=64)),
                ('description', models.CharField(max_length=2048)),
                ('title', models.CharField(max_length=128)),
                ('media_url', models.CharField(max_length=2048)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tag_name', models.CharField(max_length=64)),
                ('link_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='discord_bottachable.Link')),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.CharField(max_length=64)),
            ],
        ),
        migrations.AddField(
            model_name='link',
            name='user_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='discord_bottachable.User'),
        ),
    ]