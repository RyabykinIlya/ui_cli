from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
# from django.forms.models import model_to_dict
from django.db.models.fields.related import ManyToManyField, ForeignKey
from django.db.models.fields import DateTimeField
from django.utils.formats import date_format

from django.shortcuts import render

import json
import channels.layers
from asgiref.sync import async_to_sync

from .models import CSCU, ServerCommand

@receiver(post_save, sender=CSCU, dispatch_uid='manage_commands')
@receiver(pre_delete, sender=CSCU, dispatch_uid='manage_commands')
def manage_commands(sender, instance, **kwargs):
    '''
    Sends: lock status to the servercommand_list when a ServerCommand is modified,
           command that executed or in progress to the cscu_list page
    '''
    '''
    def to_dict(instance):

        #    instance - instance of Django model
        #    returns structure of model as dict with all Foreign Keys as their names

        #   IMPORTANT!!!
        #    Foreign models must include 'name' or 'username' fields
        #    if there needs to add more, do it in 'ForeignKey' elif block

        opts = instance._meta
        data = {}
        for f in opts.concrete_fields + opts.many_to_many:
            if isinstance(f, ManyToManyField):
                if instance.pk is None:
                    data[f.name] = []
                else:
                    data[f.name] = list(f.value_from_object(instance).values_list('pk', flat=True))
            elif isinstance(f, ForeignKey):
                # asd
                try:
                    data[f.name] = getattr(instance, f.name).name
                except AttributeError:
                    data[f.name] = getattr(instance, f.name).username
            elif isinstance(f, DateTimeField):
                date = f.value_from_object(instance)
                if date:
                    data[f.name] = date_format(f.value_from_object(instance), 'd.m.Y H:i:s')
                else:
                    data[f.name] = ''
            else:
                data[f.name] = f.value_from_object(instance)
        return data
    '''

    command = ServerCommand.objects.get(pk=instance.servercommand.pk)

    if command.lock_enable:
        if instance.locked_status is True:
            locked = True
        else:
            locked = False
    else:
        locked = None

    ######## params initialize block ########
    params = {}

    # params for servercommand_list page
    locked_commands = CSCU.objects.filter(locked_status=True)
    if locked is not None:
        params['manage_locks'] = {
            'group_name': 'commands',
            'message': {
                'command_pk': instance.servercommand.pk,
                'locked_on': ', '.join(
                    set(
                        [x.server.name for x in locked_commands if x.servercommand.id == command.id]
                    )
                )
            }
        }

    # params for cscu_list page
    print(kwargs)
    # создание
    # 'created': True, 'update_fields': None, 'raw': False, 'using': 'default'
    # update
    # 'created': False, 'update_fields': None, 'raw': False, 'using': 'default'}
    # delete
    # 'using': 'default'
    params['manage_cscu'] = {
        'group_name': 'cscus',
        'message': {'cscu_pk': instance.id,
                    'is_deleted': True if kwargs.get('created') is None else False,
                    'is_success': instance.is_success,
                    'template': render(
                        None,
                        'main/collapse_list.html',
                        {'cscu': CSCU.objects.get(pk=instance.id)}
                    ).content.decode("utf-8")  # to_dict(instance)
                    }
    }
    ######## params initialize block end ########

    channel_layer = channels.layers.get_channel_layer()

    # for each type in param send specific message to specific channels group
    for type in params:
        async_to_sync(channel_layer.group_send)(
            params[type]['group_name'],
            {
                'type': type,
                'object': params[type]['message']
            }
        )
