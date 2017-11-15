# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-11-14 09:18
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Channel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('discord_id', models.CharField(max_length=64)),
                ('listen', models.SmallIntegerField()),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Link',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('source', models.CharField(max_length=256)),
                ('description', models.CharField(max_length=2048)),
                ('title', models.CharField(max_length=128)),
                ('media_url', models.CharField(max_length=2048)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('channel_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='discord_bottachable.Channel')),
            ],
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rank', models.PositiveSmallIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Server',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('discord_id', models.CharField(max_length=64)),
                ('name', models.CharField(max_length=128)),
                ('log_channel', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='discord_bottachable.Channel')),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('discord_id', models.CharField(max_length=64)),
                ('username', models.CharField(max_length=128)),
            ],
        ),
        migrations.AddField(
            model_name='role',
            name='server_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='discord_bottachable.Server'),
        ),
        migrations.AddField(
            model_name='role',
            name='user_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='discord_bottachable.User'),
        ),
        migrations.AddField(
            model_name='link',
            name='server_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='discord_bottachable.Server'),
        ),
        migrations.AddField(
            model_name='link',
            name='tags',
            field=models.ManyToManyField(related_name='tags', to='discord_bottachable.Tag'),
        ),
        migrations.AddField(
            model_name='link',
            name='user_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='discord_bottachable.User'),
        ),
        migrations.AddField(
            model_name='channel',
            name='server_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='discord_bottachable.Server'),
        ),
    ]
