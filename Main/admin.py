from django.contrib import admin
from .models import Server, MenuItems, ServerCommand

admin.site.register(Server)
admin.site.register(MenuItems)
admin.site.register(ServerCommand)
