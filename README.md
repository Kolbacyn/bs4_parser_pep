## Парсер официальной документации с сайта python.org
![Workflow](https://github.com/Kolbacyn/bs4_parser_pep/actions/workflows/workflow.yml/badge.svg)

## Технологии:

- Python 3.9
- BeautifulSoup4
- lxml
- argparse
- logging

## Описание

Парсер позволяет получить актуальную информацию о версиях Python, авторах версий, о нововведениях в каждой из версий и получить информацию о PEP (Python Enhancement Proposal). Информацию также можно скачать в различных форматах.

## Запуск

Для начала работы необходимо клонировать репозиторий:

```bash
git clone git@github.com:Kolbacyn/bs4_parser_pep.git
```

Установить и активировать виртуальное окружение:

```bash
python -m venv venv
source venv/Scripts/activate
```

Установить зависимости из файла `requirements.txt`:

```bash
pip install -r requirements.txt
```

Перейти в папку `src`:
```bash
cd src\
```

## Режимы работы парсера

В папке `src` вызовите команду:

```bash
python main.py -h
```

Вы получите информацию о всех возможных режимах работы парсера.

- **whats-new**

Парсинг последних обновлениях с сайта [python.org](https://www.python.org/)

  ```bash
  python main.py whats-new
  ```

- **latest-versions**

Парсинг сведений о последних версиях python

  ```bash
  python main.py latest-versions
  ```

- **download**

Скачивание информации в архиве

  ```bash
  python main.py download
  ```

- **pep**

Парсин информации о статусах РЕР

  ```bash
  python main.py pep
  ```

Флаги:

`-h`, `-help` - выводит информацию о парсере и режимах его работы

`-c`, `--clear-cache` - флаг для очистки кэша запросов

`-o`, `--output` - формат вывода результата (`pretty` - в табличном формате в консоли, `file` - запись в CSV-файл)

## Примеры запуска парсера

```bash
python parser.py whats-new --output file
python parser.py latest-versions -о pretty 
python parser.py download --clear-cache
python parser.py pep
```

## Разработчик

[Зольников Юрий](https://github.com/Kolbacyn/)

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54) ![GitHub Actions](https://img.shields.io/badge/github%20actions-%232671E5.svg?style=for-the-badge&logo=githubactions&logoColor=white)
