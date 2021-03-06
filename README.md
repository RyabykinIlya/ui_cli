#ui_cli

Django version 2.0.2 'final'


Service to work with *nix-like systems, execute commands through UI-interface.

Still in dev state.

Data model: {Permission:(User(s), Contour(s), Server(s), Command(s))}

<!--Initialize Demo:
- set up any database in settings.py
- set up redis queue and add credentials into RQ_QUEUES block in settings.py
- python manage.py makemigrations
- python manage.py migrate
- python manage.py loaddata User MenuItems Contour Server ServerCommand
- login as admin/qwerty$4
-->

#EXAMPLES

Command execute window:
![Command execute window](/examples/command_execute.png?raw=true "Command execute window")
Command executions history:
![Command executions histsory](/examples/history.png?raw=true "Command executions histsory")
Locked command:
![Locked command](/examples/locked_command.png?raw=true "Locked command")
Modal window with dynamic params:
![Modal window with dynamic params](/examples/params_modal.png?raw=true "Modal window with dynamic params")

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

DONE 
15. Locked на экране выполнения комманд сделать через общий веб-сокет с каналами, чтобы в реальном времени отображался статус

#### IMPORTANT
16. https://habr.com/ru/company/oleg-bunin/blog/433476
17. Написать обработчики, которые делают запрос и вызывают методы класса хислоггер, их уже передавать на вход в rq_enqueue
Передавать в очередь только ключи, делать поиск уже непосредственно в вызове функции (без объектов моделей)
18. Сделать все обработчики задач для rq принимающими args и kwargs

20. Для передачи аргументов сделать доп таблицу, 
где для комманд будут храниться частоиспользуемые параметры, 
будет пиклист, в который можно вводить новые значения
21. Удаление cscu - отражение на экране "команды"
23. При потере соединения с сокетом закрывать функционал
