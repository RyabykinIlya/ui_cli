# ui_cli

Django version 2.0.2 'final'


Проект для работы с *nix-like системами, выполнение комманд через UI-интерфейс.
Реализована модель Контур-Сервер-Команда.


#### **TODO:**

2. Favorite сервера-команды, на главном экране часто выполняемые выводить.
Либо добавленные самим пользователем.

3. Возможность передавать аргументы в команду, после нажатия выполнить можно ввести путь/пароль и т.д.

4. Установка таймера выполнения команды или тайм-аут

5. Отмена команды. Запоминать PID запущенной, по кнопке убивать процесс?

6. Вывод ошибки с сервера, например если сервер не доступен -> показывать пользователю

7. Загружать команду в базу из файла, выполнять сразу через окно загрузки файла?
 
8. Ввод команды через модальное окно для сервера. Как быть с полномочиями?

9. Создавать веб-сокет при выполнении программы(по клику на кнопку)
При нажатии на выполнение новой команды - закрывается старый сокет, там прописать закрытие трансорта.
10. Новая модель (CSCU) Contour-Server-Command-User
В которой хранятся локи на команды, смотреть по статусу выполнения(inprogress, done), хранить историю выполненных комманд пользователями?
11. Сделать lock-комманд, новое поле - разрешить выполнять параллельно.
Если кто-то выполняет - проставляется lock в CSCU 
12. Сделать garbage-collector для cscu, чтобы при инициализации сессии проверялся статус комманд,
чтобы не оставалось залоченных комманд по ошибке