# ui_cli

Django version 2.0.2 'final'


Проект для работы с *nix-like системами, выполнение комманд через UI-интерфейс.

Реализована модель Контур-Сервер-Команда.

Initialize Demo:
- set up any database in settings.py
- set up redis queue and add credentials into RQ_QUEUES block in settings.py
- python manage.py makemigrations
- python manage.py migrate
- python manage.py loaddata User MenuItems Contour Server ServerCommand
- login as admin/qwerty$4


#### **TODO:**

2. Favorite сервера-команды, на главном экране часто выполняемые выводить.
Либо добавленные самим пользователем.

3. Возможность передавать аргументы в команду, после нажатия выполнить можно ввести путь/пароль и т.д.

4. Установка таймера выполнения команды или тайм-аут

5. Отмена команды. Запоминать PID запущенной, по кнопке убивать процесс?

6. Вывод ошибки с сервера, например если сервер не доступен -> показывать пользователю

7. Загружать команду в базу из файла, выполнять сразу через окно загрузки файла?
 
8. Создавать веб-сокет при выполнении программы(по клику на кнопку)
При нажатии на выполнение новой команды - закрывается старый сокет, там прописать закрытие трансорта.
9. Новая модель (CSCU) Contour-Server-Command-User
В которой хранятся локи на команды, смотреть по статусу выполнения(inprogress, done), хранить историю выполненных комманд пользователями?
10. Сделать lock-комманд, новое поле - разрешить выполнять параллельно.
Если кто-то выполняет - проставляется lock в CSCU 
11. Сделать garbage-collector для cscu, чтобы при инициализации сессии проверялся статус комманд,
чтобы не оставалось залоченных комманд по ошибке
12. Выполнение комманд на нескольких серверах последовательно/параллельно
13. При нажатии выполнить в окне выбираешь время выполнения/через сколько запустить(ползунком).
Для каждого пользователя есть экран с очередью задач, либо общая очередь, но отменять/переносить могут только те, кто создавал.
14. Доработать поле show_on_page для модели MenuItems
15. Locked на экране выполнения комманд сделать через общий веб-сокет с каналами, чтобы в реальном времени отображался статус

make regroup for server-command:
 cities = [
    {'name': 'Mumbai', 'population': '19,000,000', 'country': 'India'},
    {'name': 'Calcutta', 'population': '15,000,000', 'country': 'India'},
    {'name': 'New York', 'population': '20,000,000', 'country': 'USA'},
    {'name': 'Chicago', 'population': '7,000,000', 'country': 'USA'},
    {'name': 'Tokyo', 'population': '33,000,000', 'country': 'Japan'},
]

...

{% regroup cities by country as country_list %}

<ul>
    {% for country in country_list %}
        <li>{{ country.grouper }}
            <ul>
            {% for city in country.list %}
                <li>{{ city.name }}: {{ city.population }}</li>
            {% endfor %}
            </ul>
        </li>
    {% endfor %}
</ul>