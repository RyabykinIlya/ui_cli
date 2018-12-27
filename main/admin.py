from django.contrib import admin

from . import models
from .classes_override import CustomModelAdmin

admin.site.register(models.MenuItems)


class ServerInline(admin.TabularInline):
    model = models.Server
    extra = 0


@admin.register(models.Contour)
class ContourAdmin(CustomModelAdmin):
    inlines = [ServerInline, ]
    list_display = ('name', 'description')

    class Media:
        css = {
            'all': ('admin/style.css',)
        }


class ServerCommandInline(admin.TabularInline):
    model = models.ServerCommand.server.through
    extra = 1


@admin.register(models.Server)
class ServerAdmin(CustomModelAdmin):
    inlines = [ServerCommandInline, ]
    list_display = ('name_ipaddress', 'contour', 'ip_address', 'ssh_port')


@admin.register(models.ServerCommand)
class ServerCommandAdmin(CustomModelAdmin):
    search_fields = ['name', 'ip_address']

    fieldsets = (
        (None, {
            'fields': ('name', 'command', 'description', 'average_execution_time')
        }),
        ('Связи с серверами', {
            # 'classes': ('collapse',),
            'fields': ('server',),
        })
    )
    filter_horizontal = ('server',)
    readonly_fields = ('average_execution_time',)
    list_display = ('name', 'description')
    save_as = True
