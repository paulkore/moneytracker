# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('name_slug', models.SlugField(max_length=100)),
            ],
            options={
                'db_table': 'mt_event',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MoneyRecord',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('pub_date', models.DateTimeField(verbose_name='date published')),
                ('description', models.CharField(max_length=200)),
                ('amount', models.DecimalField(max_digits=10, decimal_places=2)),
                ('event', models.ForeignKey(to='trakr.Event')),
            ],
            options={
                'db_table': 'mt_money_record',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Participant',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(null=True, max_length=15)),
                ('event', models.ForeignKey(to='trakr.Event')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'mt_participant',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='moneyrecord',
            name='participant1',
            field=models.ForeignKey(to='trakr.Participant', related_name='moneyrecord_participant1'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='moneyrecord',
            name='participant2',
            field=models.ForeignKey(null=True, to='trakr.Participant', blank=True, related_name='moneyrecord_participant2'),
            preserve_default=True,
        ),
    ]
