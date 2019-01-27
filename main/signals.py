from django.db.models.signals import post_save
from django.dispatch import receiver

import json
import channels.layers
from asgiref.sync import async_to_sync

from .models import CSCU, ServerCommand


def send_message(event):
    '''
    Call back function to send message to the browser
    '''
    message = event['text']
    channel_layer = channels.layers.get_channel_layer()
    # Send message to WebSocket
    async_to_sync(channel_layer.send)(text_data=json.dumps(
        message
    ))


@receiver(post_save, sender=CSCU)#, dispatch_uid='update_commands_locks')
def update_commands_locks(sender, instance, **kwargs):
    '''
    Sends lock status to the browser when a ServerCommand is modified
    '''

    group_name = 'commands'
    command_lock_enable = ServerCommand.objects.get(pk=instance.servercommand.pk).lock_enable

    # TODO для всех возможных вариантов

    if command_lock_enable:
        if instance.locked_status is True:
            locked = True
        else:
            locked = False
    else:
        locked = False

    message = {
        'command_pk': instance.servercommand.pk,
        'locked': locked
    }

    channel_layer = channels.layers.get_channel_layer()

    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            'type': 'manage_locks',
            'text': json.dumps(message)
        }
    )
