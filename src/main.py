import logging
import re
from urllib.parse import urljoin

import requests_cache
from tqdm import tqdm

from configs import configure_argument_parser, configure_logging
from constants import (ARCHIVE_REX, BASE_DIR, EXPECTED_STATUS, MAIN_DOC_URL,
                       MISMATCHED_STATUS_MSG, PEP_LINK_REX, PEP_URL,
                       VERSION_STATUS_REX, HTMLTag)
from outputs import control_output
from utils import find_tag, get_response, get_soup


def whats_new(session):
    """Парсер информации из статей о нововведениях в Python"""
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
    results = [('Ссылка на статью', 'Заголовок', 'Редактор, Автор')]

    response = get_response(session, whats_new_url)
    if response is None:
        return None
    soup = get_soup(response)
    main_div = find_tag(
        soup,
        HTMLTag.SECTION.value,
        attrs={'id': 'what-s-new-in-python'}
    )
    div_with_ul = find_tag(
        main_div,
        HTMLTag.DIV.value,
        attrs={'class': 'toctree-wrapper'}
    )
    section_by_python = div_with_ul.find_all(
        HTMLTag.LI.value,
        attrs={'class': 'toctree-l1'}
    )

    for section in tqdm(section_by_python):
        version_a_tag = find_tag(section, HTMLTag.A.value)
        href = version_a_tag['href']
        version_link = urljoin(whats_new_url, href)
        response = get_response(session, version_link)
        if response is None:
            continue
        soup = get_soup(response)
        h1 = find_tag(soup, HTMLTag.H1.value)
        dl = find_tag(soup, HTMLTag.DL.value)
        dl_text = dl.text.replace('\n', ' ')
        results.append(
            (version_link, h1.text, dl_text)
        )
    return results


def latest_versions(session):
    """Парсер статусов версий Python"""
    results = [('Ссылка на документацию', 'Версия', 'Статус')]

    response = get_response(session, MAIN_DOC_URL)
    if response is None:
        return None
    soup = get_soup(response)
    sidebar = find_tag(
        soup,
        HTMLTag.DIV.value,
        {'class': 'sphinxsidebarwrapper'}
    )
    ul_tags = sidebar.find_all(HTMLTag.UL.value)

    for ul in ul_tags:
        if 'All versions' in ul.text:
            a_tags = ul.find_all(HTMLTag.A.value)
            break
    else:
        raise Exception('Ничего не нашлось')

    for a_tag in a_tags:
        link = a_tag['href']
        text_match = re.search(VERSION_STATUS_REX, a_tag.text)
        if text_match is not None:
            version, status = text_match.groups()
        else:
            version, status = a_tag.text, ''
        results.append(
            (link, version, status)
        )
    return results


def download(session):
    """Парсер, который скачивает архив документации Python"""
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')

    response = get_response(session, downloads_url)
    if response is None:
        return
    soup = get_soup(response)
    main_tag = find_tag(
        soup,
        HTMLTag.DIV.value,
        {'role': 'main'}
    )
    table_tag = find_tag(
        main_tag,
        HTMLTag.TABLE.value,
        {'class': 'docutils'}
    )
    pdf_a4_tag = find_tag(
        table_tag,
        HTMLTag.A.value,
        {'href': re.compile(ARCHIVE_REX)}
    )
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
    """Парсер статусов РЕР"""
    results = [('Статус', 'Количество')]
    status_total = {}
    peps_in_total = 0
    tr_tags = []

    response = get_response(session, PEP_URL)
    if response is None:
        return None
    soup = get_soup(response)
    table_tags = soup.find_all(
        HTMLTag.TABLE.value,
        attrs={'class': 'pep-zero-table docutils align-default'}
    )

    for table_tag in table_tags:
        tbody_tag = find_tag(table_tag, HTMLTag.TBODY.value)
        content = tbody_tag.find_all(HTMLTag.TR.value)
        tr_tags.extend(content)

    for tr_tag in tr_tags:
        peps_in_total += 1
        status_tag = find_tag(tr_tag, HTMLTag.TD.value)
        status_in_table = status_tag.text[1:]
        a_tag = find_tag(
            tr_tag,
            HTMLTag.A.value,
            {'href': re.compile(PEP_LINK_REX)}
        )
        href = a_tag['href']
        pep_link = urljoin(PEP_URL, href)
        pep_response = get_response(session, pep_link)
        if pep_response is None:
            return None
        pep_soup = get_soup(pep_response)
        section = find_tag(
            pep_soup,
            HTMLTag.SECTION.value,
            {'id': 'pep-content'}
        )
        dl_tag = find_tag(
            section,
            HTMLTag.DL.value,
            {'class': 'rfc2822 field-list simple'}
        )
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
