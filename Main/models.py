from django.db import models

class Server(models.Model):
    name = models.CharField(max_length=30, verbose_name='Название машины')
    ip_address = models.GenericIPAddressField(verbose_name='IP адрес машины')
    ssh_port = models.IntegerField(verbose_name='SSH порт')
    user = models.CharField(max_length=30, verbose_name="Имя пользователя")
    password = models.CharField(max_length=30, verbose_name="Пароль для подключения")

    def __str__(self):
        return '{}:{}'.format(str(self.name),str(self.ip_address))

    class Meta:
        verbose_name = 'Сервер'
        verbose_name_plural = 'Сервера'

class ServerCommand(models.Model):
    name = models.CharField(max_length=40, verbose_name='Название команды')
    server = models.ManyToManyField(Server)

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name = 'Команда'
        verbose_name_plural = 'Команды'

class MenuItems(models.Model):
    item = models.CharField(max_length=10, null=False, verbose_name="Название страницы")
    title = models.CharField(max_length=25, null=False, verbose_name="Title ссылки")
    item_id = models.CharField(max_length=10, null=False,
                               verbose_name="Id на странице")  # по нему происходит срабатывание активации пунктов меню
    order_number = models.IntegerField(verbose_name="Порядок",null=False)
    link = models.CharField(max_length=40, null=True, blank=True, verbose_name="Ссылка на страницу")
    is_sub = models.BooleanField(blank=False, verbose_name="Подкатегория?", null=False)
    is_public = models.BooleanField(verbose_name="Паблик?", default=True)

    def __str__(self):
        return str(self.item)

    class Meta:
        verbose_name = 'Меню'
        verbose_name_plural = 'Меню'
