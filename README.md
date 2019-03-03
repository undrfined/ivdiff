# ivdiff

scripts to get difference between two [Instant View](https://instantview.telegram.org) templates

## Installing

Install [python3](https://www.python.org/downloads/) and [pip](https://pypi.org/project/pip/).
Then run `git clone https://github.com/undrfined/ivdiff; cd ivdiff; pip install -r requirements.txt`.

## Auth

To authenticate run script `auth.py`:

```
py auth.py +38093******6
```
...and you're ready to go.

## ivdiff.py

get diff for one specific page

usage:

```
py ivdiff.py <Template> <Template> <URL> [-c <cookies file>] [-b <browser>]
```

...where `<Template>` is a template number if it was submitted to contest (for example `45`) or filename with the template code(for example `file.xpath`). **Please do a backup of your code before using filename as one of the templates**
`<URL>` is an URL to diff.
`<browser>` is a browser name (according to [docs](https://docs.python.org/3/library/webbrowser.html)) or path to program to open file

## batchdiff.py

get diff for a lot of pages from file

usage:

```
py batchdiff.py <Template> <Template> <List of URLs> [-c <cookies file>] [-p <pool size>]
```

...where `<List of URLs>` is a filename with list of all the urls you want to diff and `<pool size>` is count of threads you want to use (default 5)

## spider.py

collect all the URLs automatically and get diff for all of them

usage:

```
py spider.py <Template> <Template> <domain> [-c <cookies file>] [-p <pool size>] [-b <browser>]
```

...where `<domain>` is a domain name (for example `5minutes.rtl.lu`)
`<browser>` is a browser name (according to [docs](https://docs.python.org/3/library/webbrowser.html)) or path to program to open file

# russian

# ivdiff

скрипты для получения разницы между двумя темплейтами [Instant View](https://instantview.telegram.org)

## Установка

Установите [python3](https://www.python.org/downloads/) и [pip](https://pypi.org/project/pip/).
Затем в терминале напишите `git clone https://github.com/undrfined/ivdiff; cd ivdiff; pip install -r requirements.txt`.

## Авторизация

Для авторизации запустите скрипт `auth.py`:

```
py auth.py +38093******6
```
...ну а дальше по инструкции

## ivdiff.py

получить разницу для определенной страницы

юзать вот так:

```
py ivdiff.py <Template> <Template> <URL> [-c <cookies file>] [-b <browser>]
```

...где `<Template>` это номер опубликованого темплейта (например `45`) или название файла с исходником(например `file.xpath`). **Обязательно делайте бекап перед использованием файла исходника так как оно перезапишет ваш текущий код**
`<URL>` это ссылка на страницу
`<browser>` это название браузера (из [документации](https://docs.python.org/3/library/webbrowser.html)) или путь к программе которая откроет результат

## batchdiff.py

получить разницу для массива ссылок

юзать вот так:

```
py batchdiff.py <Template> <Template> <List of URLs> [-c <cookies file>] [-p <pool size>]
```

...где `<List of URLs>` это название файла со ссылками и `<pool size>` это количество потоков которое вы хотите использовать (стандартно 5)

## spider.py

автоматически собирать все ссылки с домена и смотреть разницу

юзать вот так:

```
py spider.py <Template> <Template> <domain> [-c <cookies file>] [-p <pool size>] [-b <browser>]
```

...где `<domain>` это домен (например `5minutes.rtl.lu`)
`<browser>` это название браузера (из [документации](https://docs.python.org/3/library/webbrowser.html)) или путь к программе которая откроет результат
