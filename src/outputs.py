import csv
import datetime as dt
import logging

from prettytable import PrettyTable

from constants import BASE_DIR, DATETIME_FORMAT, ENCODING_UTF, OutputType


def control_output(results, cli_args):
    """В зависимости от примененного флага, устанавливает тип вывода"""
    output = cli_args.output
    if output == OutputType.PRETTY:
        pretty_output(results)
    elif output == OutputType.FILE:
        file_output(results, cli_args)
    else:
        default_output(results)


def default_output(results):
    """Стандартный построчный вывод в консоли"""
    for row in results:
        print(*row)


def pretty_output(results):
    """Вывод результата в консоли в виде таблицы"""
    table = PrettyTable()
    table.field_names = results[0]
    table.align = 'l'
    table.add_rows(results[1:])
    print(table)


def file_output(results, cli_args):
    """Сохранение результатата в файл в формате .csv"""
    result_dir = BASE_DIR / 'results'
    result_dir.mkdir(exist_ok=True)
    parser_mode = cli_args.mode
    now = dt.datetime.now()
    now_formatted = now.strftime(DATETIME_FORMAT)
    filename = f'{parser_mode}_{now_formatted}.csv'
    file_path = result_dir / filename
    with open(file_path, 'w', encoding=ENCODING_UTF) as file:
        writer = csv.writer(file, dialect='unix')
        writer.writerows(results)
    logging.info(f'Файл с результатами был сохранён: {file_path}')
