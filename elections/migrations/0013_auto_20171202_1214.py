# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-12-02 08:14
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('elections', '0012_candidate_profilepicture'),
    ]

    operations = [
        migrations.AlterField(
            model_name='candidate',
            name='ProfilePicture',
            field=models.ImageField(blank=True, null=True, upload_to='profilepics/'),
        ),
    ]
