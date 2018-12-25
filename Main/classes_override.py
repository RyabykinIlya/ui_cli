from channels.generic.websocket import WebsocketConsumer


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
