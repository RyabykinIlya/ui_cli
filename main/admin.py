from django.contrib import admin

from . import models
from .classes_override import CustomModelAdmin


################################## inlines ##################################
class ServerInline(admin.TabularInline):
    model = models.Server
    extra = 0
    exclude = ('last_upd_by',)


'''
class ContourInline(admin.StackedInline):
    model = models.Contour.permissions.through
    can_delete = False
    verbose_name_plural = 'Контуры'
'''


class ServerCommandInline(admin.TabularInline):
    model = models.ServerCommand.server.through
    extra = 0
    verbose_name_plural = 'Команды'


################################## inlines end ##################################

@admin.register(models.Permission)
class PermissionAdmin(CustomModelAdmin):
    model = models.Permission
    # inlines = (ContourInline,)
    filter_horizontal = ('user', 'contour', 'server', 'servercommand')


@admin.register(models.MenuItems)
class MenuItemsAdmin(CustomModelAdmin):
    model = models.MenuItems


@admin.register(models.Contour)
class ContourAdmin(CustomModelAdmin):
    inlines = [ServerInline, ]
    list_display = ('name', 'description')

    # filter_horizontal = ('permissions',)

    class Media:
        css = {
            'all': ('admin/style.css',)
        }


@admin.register(models.Server)
class ServerAdmin(CustomModelAdmin):
    inlines = [ServerCommandInline, ]
    list_display = ('name_ipaddress', 'contour', 'ip_address', 'ssh_port')
    # filter_horizontal = ('permissions',)


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
    ''',
    ('Полномочия', {
        'fields': ('permissions',),
    })
    '''
    filter_horizontal = ('server',)
    readonly_fields = ('average_execution_time',)
    list_display = ('name', 'description')
