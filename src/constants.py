from enum import Enum
from pathlib import Path

MAIN_DOC_URL = 'https://docs.python.org/3/'
PEP_URL = 'https://peps.python.org/'
BASE_DIR = Path(__file__).parent
DATETIME_FORMAT = '%Y-%m-%d_%H-%M-%S'
LOG_FORMAT = '"%(asctime)s - [%(levelname)s] - %(message)s"'
LOG_DT_FORMAT = '%d.%m.%Y %H:%M:%S'
EXPECTED_STATUS = {
    'A': ('Active', 'Accepted'),
    'D': ('Deferred',),
    'F': ('Final',),
    'P': ('Provisional',),
    'R': ('Rejected',),
    'S': ('Superseded',),
    'W': ('Withdrawn',),
    '': ('Draft', 'Active'),
}
MISMATCHED_STATUS_MSG = ('\n'
                         'Несовпадающие статусы:\n'
                         '{link}\n'
                         'Статус в карточке: {page_status}\n'
                         'Ожидаемые статусы: [{review_status}]')
ENCODING_UTF = 'utf-8'

# Регулярные выражения:
# Выражение для поиска информации о версии Рython и ее текущем статусе.
VERSION_STATUS_REX = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'
# Выражение для поиска имени аржива.
ARCHIVE_REX = r'.+pdf-a4\.zip$'
# Выражение для поиска ссылки на РЕР.
PEP_LINK_REX = r'pep-\d+\/'


class OutputType(str, Enum):
    """Выбор режимов вывода"""
    PRETTY = 'pretty'
    FILE = 'file'


class HTMLTag(str, Enum):
    """HTML-теги"""
    A = 'a'
    DIV = 'div'
    DL = 'dl'
    H1 = 'h1'
    LI = 'li'
    SECTION = 'section'
    TABLE = 'table'
    TBODY = 'tbody'
    TD = 'td'
    TR = 'tr'
    UL = 'ul'
