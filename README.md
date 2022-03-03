Это простое приложение на Python.

Простите за язык, никогда таких текстов на русском не писал и не читпл,
а времени разбираться в русской терминологии нет )))

Чтобы запустить приложение, наберите: gunicorn simple_wsgi:application

Корневой URL приложения выводит список переданных в него параметров запроса GET,
осуществляя их рендер в представлении index.html.
Пример: http://127.0.0.1:8000

URL первого уровня от корня выводят:

- если путь совпадает с именем параметра - страницу с детализацией параметра,
  осуществляя ее рендер в представлении parameter.html;
  Пример: http://127.0.0.1:8000/HTTP_ACCEPT_LANGUAGE

- если путь не совпадает с именем параметра - произвольную страницу .html
  с совпадающим именем в текущей папке;
  Пример: http://127.0.0.1:8000/anyURL

- сообщение об ошибке, если не найдены ни параметр, ни страница.
  Пример: http://127.0.0.1:8000/HTTP_ACCEPT_LA

URL второго и более уровня от корня выводит сообщение об ошибке.
Пример: 127.0.0.1:8000/HTTP_ACCEPT_LANGUAGE/hjhgjhg

Сообщение об ошибке выводится через рендер представления error404.html.

Для демонстрации в проекте представлена произвольная страница test.html ,
которую можно посмотреть, задав ее имя как URL первого уровня.
Пример: http://127.0.0.1:8000/test

Предусмотрена обработка исключения при отсутствии ожидаемого файла .html -
выводится минимальная осмысленная информация в соответствии с требуемой операцией.