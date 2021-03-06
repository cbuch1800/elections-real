# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-12-12 07:04
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('elections', '0013_auto_20171202_1214'),
    ]

    operations = [
        migrations.CreateModel(
            name='Result',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Results', models.TextField()),
                ('ElectionID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='elections.Election')),
            ],
            options={
                'permissions': (('can_view_results', 'Can view election results'),),
            },
        ),
    ]
