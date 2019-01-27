from django.db import models
from django.contrib.auth.models import User
from django.db.models.query_utils import Q
from datetime import datetime

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
    def get(self, *args, **kwargs):
        # do not restrict for superuser
        if 'permission__user' in kwargs:
            if getattr(kwargs['permission__user'], 'is_superuser'):
                kwargs.pop('permission__user')
        return super().get(*args, **kwargs)

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
    contour = models.ForeignKey(Contour, related_name='server', on_delete=models.CASCADE, verbose_name='Контур')

    def get_absolute_url(self):
        return '/server/%i/' % self.id

    def name_ipaddress(self):
        return '{}: {}'.format(str(self.name), str(self.ip_address))

    name_ipaddress.short_description = 'Название машины: IP'

    def __str__(self):
        # return '{}:{}'.format(str(self.name), str(self.ip_address))
        return str(self.name)

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
    lock_enable = models.BooleanField(verbose_name='Запретить выполнять параллельно', default=False)

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name = 'Команда'
        verbose_name_plural = 'Команды'


class MenuItems(ModelWithUser, models.Model):
    item = models.CharField(max_length=20, null=False, verbose_name='Название страницы')
    title = models.CharField(max_length=40, null=False, verbose_name='Title ссылки')
    item_id = models.CharField(max_length=10, null=False, verbose_name='Id на странице',
                               help_text='По этому параметру происходит активация пунктов меню'
                                         '<br>Если url== */commands/history/, то нужно указать history')
    order_by = models.IntegerField(verbose_name='Порядок', null=False)
    link = models.CharField(max_length=40, null=True, blank=True, verbose_name='Ссылка на страницу')
    is_sub = models.BooleanField(blank=False, verbose_name='Подкатегория?', null=False)
    is_public = models.BooleanField(verbose_name='Паблик?', default=True)
    ''' TODO
    show_on_page = models.CharField(max_length=50, null=True, verbose_name='Показывать на страницах',
                                    help_text='Укажите шаблон ссылки на страницу, для которой необходимо отображать'
                                              'данную ссылку в меню')
    '''

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

class CSCU(models.Model):
    """
    Contour-Server-Command-User
    Model for В которой хранятся локи на команды,
    смотреть по статусу выполнения(inprogress, done),
    store history of executed command by users
    """
    contour = models.ForeignKey(Contour, verbose_name='Контур', on_delete=models.SET_NULL, null=True)
    server = models.ForeignKey(Server, verbose_name='Сервер', on_delete=models.SET_NULL, null=True)
    servercommand = models.ForeignKey(ServerCommand, verbose_name='Команда', on_delete=models.SET_NULL, null=True)
    user = models.ForeignKey(User, verbose_name='Пользователь', on_delete=models.SET_NULL, null=True)
    locked_status = models.BooleanField(verbose_name='Выполняется другим пользователем', default=False)
    start_time = models.DateTimeField(verbose_name='Время начала выполнения', default=datetime.now())
    end_time = models.DateTimeField(verbose_name='Время завершения выполнения', null=True)
    cmd_output = models.TextField(verbose_name='Результат выполнения команды', null=True)
    is_success = models.NullBooleanField(verbose_name='Статус выполнения', null=True)