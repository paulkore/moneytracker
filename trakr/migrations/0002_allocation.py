# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('moneytracker', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Allocation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('money_record', models.ForeignKey(to='moneytracker.MoneyRecord')),
                ('participant', models.ForeignKey(to='moneytracker.Participant')),
            ],
            options={
                'db_table': 'mt_allocation',
            },
            bases=(models.Model,),
        ),
    ]
