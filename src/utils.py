import logging

from bs4 import BeautifulSoup
from requests import RequestException

from constants import ENCODING_UTF
from exceptions import ParserFindTagException


def get_response(session, url):
    """загрузка страницы с перехватом ошибки RequestException"""
    try:
        response = session.get(url)
        response.encoding = ENCODING_UTF
        return response
    except RequestException:
        logging.exception(
            f'Возникла ошибка при загрузке страницы {url}',
            stack_info=True
        )


def find_tag(soup, tag, attrs=None):
    """Поиск тега"""
    search_tag = soup.find(tag, attrs=(attrs or {}))
    if search_tag is None:
        error_msg = f'Не найден тег {tag} {attrs}'
        logging.error(error_msg, stack_info=True)
        raise ParserFindTagException(error_msg)
    return search_tag


def get_soup(response):
    """Получение объекта BeautifulSoup"""
    return BeautifulSoup(response.text, features='lxml')
