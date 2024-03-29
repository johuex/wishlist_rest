#  Проект "Список желаний - Wishlist"

[Wiki-заметка на Notion](https://www.notion.so/8f71fa1080214f029ef5c3067897f616?v=1850288b4e044fb785f10074f697403f)

[Нынешний вариант на Heroku](https://wishlist0.herokuapp.com)


### Содержимое данного репозитория

* `README.md` - файл, который вы сейчас читаете;
* `other_docs/tz.md` - техническое задание от курсовой работы в формате markdown;
* `run.py` - файл, запускающий веб-приложение;
* `app/` - каталог, в котором содержатся файлы с исходным кодом веб-приложения;
* `scripts/` - каталог, в котором содержатся sql-скрипты: `create_db.sql` - создание БД, `insert_data.sql` - добавление начальных данных в БД.
* `app/static` - каталог с html-шаблонами для веб-приложения и картинками по умолчанию;
* `app/forms.py` - файл с формами для html-шаблонов;
* `app/models.py` - файл ;
* `app/routes.py` - файл с основной логикой работы приложения (пока без API);
* `app/__init__.py` - файл инициализации;

### Что реализовано
* Регистрация авторизация;
* Логика запросов в друзья и запросов в друзья;
* Добавление и редактирование (кроме загрузки картинок) желаний и списков;
* Новостная лента друзей с последними желаниями;
* Возможность выбрать желание друга "в исполнение";

### Планы
* Добавить API;
* Добавить групповые списки;
* Переделать доступ к желанию, выбранному для исполнения;
* Доделать логику с исполненым желанием;
* Перенести с Heroku на Amazon (S3 + RDS + EC2).
