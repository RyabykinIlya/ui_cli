from django.contrib import admin
from .models import Server, MenuItems, ServerCommand


class ServerCommandInline(admin.TabularInline):
    model = ServerCommand.server.through
    extra = 1


class ServerAdmin(admin.ModelAdmin):
    inlines = [ServerCommandInline, ]
    exclude = ('server',)
    readonly_fields = ('average_execution_time',)
    search_fields = ['name']
    list_display = ('name', 'description', 'average_execution_time')


class ServerCommandAdmin(admin.ModelAdmin):
    inlines = [ServerCommandInline, ]
    search_fields = ['name', 'ip_address']
    list_display = ('name', 'ip_address', 'ssh_port')
    # show filter column at the right
    # list_filter = ('name',)


admin.site.register(Server, ServerCommandAdmin)
admin.site.register(ServerCommand, ServerAdmin)
admin.site.register(MenuItems)
