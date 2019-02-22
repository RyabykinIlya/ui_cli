import json
from django.contrib import admin
from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer

class CustomModelAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        obj.last_upd_by = request.user
        super().save_model(request, obj, form, change)

    readonly_fields = ('last_upd_by',)
    save_as = True

    def get_list_display(self, request):
        return self.list_display + ('last_upd_by',)

    class Media:
        css = {
            'all': ('admin/style.css',)
        }

class WebsocketConsumerCustom(WebsocketConsumer):
    # Overriding WebsocketConsumer class for better functionality.

    def send_msg(self, type, object):
        '''
        type - info or message
        msg - any string
        '''
        self.send(text_data=json.dumps({
            str(type): object
        }))

class AsyncWebsocketConsumerCustom(AsyncWebsocketConsumer):
    # Overriding WebsocketConsumer class for better functionality.

    async def send_msg(self, type, object):
        '''
        type - info or message
        msg - any string
        '''
        await self.send(text_data=json.dumps({
            str(type): object
        }))

''' not used
class WebsocketConsumerCustom(WebsocketConsumer):
    # Overriding WebsocketConsumer class for better functionality.

    def get_websocket_kwargs(self, socket, key):
        # Custom method for getting kwargs key using one function.

        value = socket.scope['url_route']['kwargs'].get(key, -1)
        if value == -1:
            raise KeyError('Key {} does not exist in '
                           'socket->scope(dict)->url_route(dict)->kwargs(dict) you passed from JS '
                           'web-socket initialization'.format(key))
        else:
            return value

class AsyncWebsocketConsumerCustom(AsyncWebsocketConsumer):
    # Overriding WebsocketConsumer class for better functionality.

    def get_websocket_kwargs(self, socket, key):
        # Custom method for getting kwargs key using one function.

        value = socket.scope['url_route']['kwargs'].get(key, -1)
        if value == -1:
            raise KeyError('Key {} does not exist in '
                           'socket->scope(dict)->url_route(dict)->kwargs(dict) you passed from JS '
                           'web-socket initialization'.format(key))
        else:
            return value
'''