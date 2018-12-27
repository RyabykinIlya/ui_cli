from channels.generic.websocket import WebsocketConsumer
from django.contrib import admin


class CustomModelAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        obj.last_upd_by = request.user
        super().save_model(request, obj, form, change)

    readonly_fields = ('last_upd_by',)

    def get_list_display(self, request):
        return self.list_display + ('last_upd_by',)

    class Media:
        css = {
            'all': ('admin/style.css',)
        }


class WebsocketConsumerCustom(WebsocketConsumer):
    'Overriding WebsocketConsumer class for better functionality.'

    def get_websocket_kwargs(self, socket, key):
        'Custom method for getting kwargs key using one function.'

        value = socket.scope['url_route']['kwargs'].get(key, 0)
        if value == 0:
            raise KeyError('Key {} does not exist in '
                           'socket->scope(dict)->url_route(dict)->kwargs(dict) you passed.'.format(key))
        else:
            return value
