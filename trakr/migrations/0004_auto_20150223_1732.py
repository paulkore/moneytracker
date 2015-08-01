# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trakr', '0003_auto_20150223_1638'),
    ]

    operations = [
        migrations.RenameField(
            model_name='participant',
            old_name='is_primary',
            new_name='is_default',
        ),
    ]
