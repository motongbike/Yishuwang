# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-11-06 10:29
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_auto_20161101_0835'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='contact',
            field=models.CharField(default='暂无', max_length=50),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='major',
            field=models.CharField(default='暂无', max_length=128),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='school',
            field=models.CharField(default='暂无', max_length=51200),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='description',
            field=models.CharField(blank=True, default='暂无', max_length=128),
        ),
    ]
