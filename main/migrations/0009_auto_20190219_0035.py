# Generated by Django 2.0.2 on 2019-02-18 21:35

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('django_celery_results', '0003_auto_20181106_1101'),
        ('main', '0008_auto_20190217_0120'),
    ]

    operations = [
        migrations.AddField(
            model_name='cscu',
            name='task_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='django_celery_results.TaskResult', verbose_name='Задача celery'),
        ),
        migrations.AlterField(
            model_name='cscu',
            name='cmd_output',
            field=models.TextField(blank=True, null=True, verbose_name='Результат выполнения команды'),
        ),
        migrations.AlterField(
            model_name='cscu',
            name='end_time',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Время завершения выполнения'),
        ),
        migrations.AlterField(
            model_name='cscu',
            name='parameters',
            field=models.TextField(blank=True, null=True, verbose_name='Параметры запуска'),
        ),
        migrations.AlterField(
            model_name='cscu',
            name='start_time',
            field=models.DateTimeField(default=datetime.datetime(2019, 2, 19, 0, 35, 43, 567594), verbose_name='Время начала выполнения'),
        ),
    ]