from django.db import models


class Contour(models.Model):
    name = models.CharField(max_length=75, verbose_name='Название контура')
    description = models.TextField(verbose_name='Описание контура', blank=True, null=True)

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name = 'Контур'
        verbose_name_plural = 'Контуры'


class Server(models.Model):
    name = models.CharField(max_length=30, verbose_name='Название машины')
    ip_address = models.GenericIPAddressField(verbose_name='IP адрес машины')
    ssh_port = models.IntegerField(verbose_name='SSH порт')
    user = models.CharField(max_length=30, verbose_name='Имя пользователя')
    password = models.CharField(max_length=30, verbose_name='Пароль для подключения')
    contour = models.ForeignKey(Contour, related_name='severs', on_delete=models.CASCADE, verbose_name='Контур')

    def get_absolute_url(self):
        return '/server/%i/' % self.id

    def __str__(self):
        return '{}:{}'.format(str(self.name), str(self.ip_address))

    class Meta:
        verbose_name = 'Сервер'
        verbose_name_plural = 'Сервера'


class ServerCommand(models.Model):
    name = models.CharField(max_length=40, verbose_name='Название команды')
    command = models.TextField(max_length=2000, verbose_name='Команда для выполнения')
    description = models.TextField(verbose_name='Описание команды', blank=True, null=True)
    average_execution_time = models.FloatField(verbose_name='Среднее время выполнения команды', default=1.0)
    server = models.ManyToManyField(Server, related_name='commands', verbose_name='Сервер')

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name = 'Команда'
        verbose_name_plural = 'Команды'


class MenuItems(models.Model):
    item = models.CharField(max_length=15, null=False, verbose_name='Название страницы')
    title = models.CharField(max_length=25, null=False, verbose_name='Title ссылки')
    item_id = models.CharField(max_length=10, null=False,
                               verbose_name='Id на странице')  # по нему происходит срабатывание активации пунктов меню
    order_number = models.IntegerField(verbose_name='Порядок', null=False)
    link = models.CharField(max_length=40, null=True, blank=True, verbose_name='Ссылка на страницу')
    is_sub = models.BooleanField(blank=False, verbose_name='Подкатегория?', null=False)
    is_public = models.BooleanField(verbose_name='Паблик?', default=True)

    def __str__(self):
        return str(self.item)

    class Meta:
        verbose_name = 'Меню'
        verbose_name_plural = 'Меню'


from django.contrib.auth.models import User


class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.CharField(max_length=100)


'''
class Permission(models.Model):
    """
    The permissions system provides a way to assign permissions to specific
    users and groups of users.

    The permission system is used by the Django admin site, but may also be
    useful in your own code. The Django admin site uses permissions as follows:

        - The "add" permission limits the user's ability to view the "add" form
          and add an object.
        - The "change" permission limits a user's ability to view the change
          list, view the "change" form and change an object.
        - The "delete" permission limits the ability to delete an object.

    Permissions are set globally per type of object, not per specific object
    instance. It is possible to say "Mary may change news stories," but it's
    not currently possible to say "Mary may change news stories, but only the
    ones she created herself" or "Mary may only change news stories that have a
    certain status or publication date."

    Three basic permissions -- add, change and delete -- are automatically
    created for each Django model.
    """
    name = models.CharField(_('name'), max_length=255)
    content_type = models.ForeignKey(
        ContentType,
        models.CASCADE,
        verbose_name=_('content type'),
    )
    codename = models.CharField(_('codename'), max_length=100)
    objects = PermissionManager()

    class Meta:
        verbose_name = _('permission')
        verbose_name_plural = _('permissions')
        unique_together = (('content_type', 'codename'),)
        ordering = ('content_type__app_label', 'content_type__model',
                    'codename')

    def __str__(self):
        return "%s | %s | %s" % (
            self.content_type.app_label,
            self.content_type,
            self.name,
        )

    def natural_key(self):
        return (self.codename,) + self.content_type.natural_key()
    natural_key.dependencies = ['contenttypes.contenttype']
'''
