# Generated by Django 2.0.2 on 2019-02-16 22:20

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0007_auto_20190209_1116'),
    ]

    operations = [
        migrations.AddField(
            model_name='cscu',
            name='parameters',
            field=models.TextField(null=True, verbose_name='Параметры запуска'),
        ),
        migrations.AlterField(
            model_name='cscu',
            name='start_time',
            field=models.DateTimeField(default=datetime.datetime(2019, 2, 17, 1, 20, 54, 122886), verbose_name='Время начала выполнения'),
        ),
        migrations.AlterField(
            model_name='servercommand',
            name='with_parameters',
            field=models.BooleanField(default=False, help_text='\n                В поле "Команда для выполнения" динамические параметры должны быть оформлены следующим образом:\n                <br>execute command %PARAM_NAME|Название_параметра%,\n                <br>где PARAM_NAME - динамический параметр, который пользователь введёт при выполнении,\n                    <br>Название_параметра - название поля, в которое польхователь введёт параметр.', verbose_name='Возможность передать параметры в команду'),
        ),
    ]
