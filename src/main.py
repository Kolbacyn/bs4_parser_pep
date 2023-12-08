import logging
import re
from urllib.parse import urljoin

import requests_cache
from bs4 import BeautifulSoup
from tqdm import tqdm

from configs import configure_argument_parser, configure_logging
from constants import (BASE_DIR, MAIN_DOC_URL,
                       PEP_URL, EXPECTED_STATUS, MISMATCHED_STATUS_MSG)
from outputs import control_output
from utils import get_response, find_tag


def whats_new(session):
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
    response = get_response(session, whats_new_url)
    if response is None:
        return
    soup = BeautifulSoup(response.text, features='lxml')
    main_div = find_tag(soup, 'section', attrs={'id': 'what-s-new-in-python'})
    div_with_ul = find_tag(main_div, 'div', attrs={'class': 'toctree-wrapper'})
    section_by_python = div_with_ul.find_all('li',
                                             attrs={'class': 'toctree-l1'})
    results = [('Ссылка на статью', 'Заголовок', 'Редактор, Автор')]
    for section in tqdm(section_by_python):
        version_a_tag = find_tag(section, 'a')
        href = version_a_tag['href']
        version_link = urljoin(whats_new_url, href)
        response = get_response(session, version_link)
        if response is None:
            continue
        soup = BeautifulSoup(response.text, features='lxml')
        h1 = find_tag(soup, 'h1')
        dl = find_tag(soup, 'dl')
        dl_text = dl.text.replace('\n', ' ')
        results.append(
            (version_link, h1.text, dl_text)
        )
    print(results)
    return results


def latest_versions(session):
    pattern = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'
    response = get_response(session, MAIN_DOC_URL)
    if response is None:
        return
    soup = BeautifulSoup(response.text, features='lxml')
    sidebar = find_tag(soup, 'div', {'class': 'sphinxsidebarwrapper'})
    ul_tags = sidebar.find_all('ul')
    for ul in ul_tags:
        if 'All versions' in ul.text:
            a_tags = ul.find_all('a')
            break
    else:
        raise Exception('Ничего не нашлось')
    results = [('Ссылка на документацию', 'Версия', 'Статус')]
    for a_tag in a_tags:
        link = a_tag['href']
        text_match = re.search(pattern, a_tag.text)
        if text_match is not None:
            version, status = text_match.groups()
        else:
            version, status = a_tag.text, ''
        results.append(
            (link, version, status)
        )
    return results


def download(session):
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')
    response = get_response(session, downloads_url)
    if response is None:
        return
    soup = BeautifulSoup(response.text, features='lxml')
    main_tag = find_tag(soup, 'div', {'role': 'main'})
    table_tag = find_tag(main_tag, 'table', {'class': 'docutils'}) 
    pdf_a4_tag = find_tag(table_tag,
                          'a',
                          {'href': re.compile(r'.+pdf-a4\.zip$')})
    pdf_a4_link = pdf_a4_tag['href']
    archive_url = urljoin(downloads_url, pdf_a4_link)
    filename = archive_url.split('/')[-1]
    downloads_dir = BASE_DIR / 'downloads'
    downloads_dir.mkdir(exist_ok=True)
    archive_path = downloads_dir / filename
    response = get_response(session, archive_url)
    if response is None:
        return
    with open(archive_path, 'wb') as file:
        file.write(response.content)
    logging.info(f'Архив был загружен и сохранён: {archive_path}')


def pep(session):
    results = [('Статус', 'Количество')]
    status_total = {}
    peps_in_total = 0
    tr_tags = []

    response = get_response(session, PEP_URL)
    if response is None:
        return
    soup = BeautifulSoup(response.text, 'lxml')
    table_tags = soup.find_all(
        'table',
        attrs={'class': 'pep-zero-table docutils align-default'}
    )

    for table_tag in table_tags:
        tbody_tag = find_tag(table_tag, 'tbody')
        content = tbody_tag.find_all('tr')
        tr_tags.extend(content)

    for tr_tag in tr_tags:
        peps_in_total += 1
        status_tag = find_tag(tr_tag, 'td')
        status_in_table = status_tag.text[1:]
        a_tag = find_tag(tr_tag, 'a', {'href': re.compile(r'pep-\d+\/')})
        href = a_tag['href']
        pep_link = urljoin(PEP_URL, href)
        pep_response = get_response(session, pep_link)
        if pep_response is None:
            return
        pep_soup = BeautifulSoup(pep_response.text, 'lxml')
        section = find_tag(pep_soup, 'section', {'id': 'pep-content'})
        dl_tag = find_tag(section, 'dl', {'class': 'rfc2822 field-list simple'})
        pep_status = dl_tag.find(
            string='Status').parent.find_next_sibling('dd').string
        if pep_status not in status_total:
            status_total[pep_status] = 1
        if pep_status in status_total:
            status_total[pep_status] += 1
        if pep_status not in EXPECTED_STATUS[status_in_table]:
            info_message = (MISMATCHED_STATUS_MSG.format(
                link=pep_link,
                page_status=pep_status,
                review_status=EXPECTED_STATUS[status_in_table])
            )
            logging.info(info_message)
    for status in status_total:
        results.append(
            (status, status_total[status])
        )
    results.append(('Total', peps_in_total))
    return results


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep
}


def main():
    configure_logging()
    logging.info('Парсер запущен!')
    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    args = arg_parser.parse_args()
    logging.info(f'Аргументы командной строки: {args}')
    session = requests_cache.CachedSession()
    if args.clear_cache:
        session.cache.clear()
    parser_mode = args.mode
    results = MODE_TO_FUNCTION[parser_mode](session)
    if results is not None:
        control_output(results, args)
    logging.info('Парсер завершил работу.')


if __name__ == '__main__':
    main()
