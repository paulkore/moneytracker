# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trakr', '0005_moneyrecord_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='allocation',
            name='amount',
            field=models.DecimalField(max_digits=10, null=True, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='allocation',
            name='type',
            field=models.IntegerField(default=1),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='moneyrecord',
            name='type',
            field=models.IntegerField(default=1),
            preserve_default=True,
        ),
    ]
