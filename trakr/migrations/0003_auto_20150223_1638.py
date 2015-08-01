# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trakr', '0002_allocation'),
    ]

    operations = [
        migrations.AddField(
            model_name='participant',
            name='is_primary',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='event',
            name='name_slug',
            field=models.SlugField(max_length=100, default='this-value-is-auto-generated'),
            preserve_default=True,
        ),
    ]
