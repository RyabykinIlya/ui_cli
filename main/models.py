from django.db import models
from django.contrib.auth.models import User
from django.db.models.query_utils import Q


class ModelWithUser(models.Model):
    last_upd_by = models.ForeignKey(User, verbose_name='Кем изменено', on_delete=models.SET_NULL,
                                    blank=True, null=True)

    class Meta:
        abstract = True


################################## permissions additional classes ##################################
class RestrictedQuerySet(models.query.QuerySet):
    ' used for model manager to restrict selected rows '

    def get_restricted(self, user=None):
        if getattr(user, 'is_superuser'):
            return self
        else:
            return self.filter(permission__user=user)


class RestrictedManager(models.Manager):
    ' custom manager to override QuerySet '

    def get_queryset(self):
        return RestrictedQuerySet(self.model, using=self._db)


class RestrictedModel(models.Model):
    ' custom model class with custom manager cobjects used for filtering rows from db '
    objects = models.Manager()
    cobjects = RestrictedManager()

    class Meta:
        abstract = True


################################## permissions additional classes end ##################################

class Contour(ModelWithUser, RestrictedModel, models.Model):
    name = models.CharField(max_length=75, verbose_name='Название контура')
    description = models.TextField(verbose_name='Описание контура', blank=True, null=True)
    order_by = models.IntegerField(verbose_name='Порядок отображения', default=999)

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name = 'Контур'
        verbose_name_plural = 'Контуры'


class Server(ModelWithUser, RestrictedModel, models.Model):
    name = models.CharField(max_length=30, verbose_name='Название машины')
    ip_address = models.GenericIPAddressField(verbose_name='IP адрес машины')
    ssh_port = models.IntegerField(verbose_name='SSH порт')
    user = models.CharField(max_length=30, verbose_name='Имя пользователя')
    password = models.CharField(max_length=30, verbose_name='Пароль для подключения')
    contour = models.ForeignKey(Contour, related_name='severs', on_delete=models.CASCADE, verbose_name='Контур')

    def get_absolute_url(self):
        return '/server/%i/' % self.id

    def name_ipaddress(self):
        return '{}: {}'.format(str(self.name), str(self.ip_address))

    name_ipaddress.short_description = 'Название машины: IP'

    def __str__(self):
        return '{}:{}'.format(str(self.name), str(self.ip_address))

    class Meta:
        verbose_name = 'Сервер'
        verbose_name_plural = 'Сервера'
        unique_together = (('ip_address', 'ssh_port'),)


class ServerCommand(ModelWithUser, RestrictedModel, models.Model):
    name = models.CharField(max_length=40, verbose_name='Название команды')
    command = models.TextField(max_length=2000, verbose_name='Команда для выполнения', help_text='''
    Введите команду для выполнения на сервере<br>
    Вы можете ввести custom_command для того, чтобы пользователь сам ввёл команду''')
    description = models.TextField(verbose_name='Описание команды', blank=True, null=True)
    average_execution_time = models.FloatField(verbose_name='Среднее время выполнения команды', default=1.0)
    server = models.ManyToManyField(Server, related_name='commands', verbose_name='Сервер')

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name = 'Команда'
        verbose_name_plural = 'Команды'


class MenuItems(ModelWithUser, models.Model):
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


class Permission(ModelWithUser, models.Model):
    name = models.CharField(max_length=75, verbose_name='Название полномочия')
    contour = models.ManyToManyField(Contour, verbose_name='Контуры', blank=True)
    server = models.ManyToManyField(Server, verbose_name='Сервера', blank=True)
    servercommand = models.ManyToManyField(ServerCommand, verbose_name='Команды', blank=True)
    user = models.ManyToManyField(User, related_name='user_permission', verbose_name='Пользователь')

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name = 'Полномочие'
        verbose_name_plural = 'Полномочия'
