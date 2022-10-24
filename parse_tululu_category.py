import os
import re
import sys
import json
import argparse
import logging
from logging.handlers import RotatingFileHandler
from urllib.parse import urljoin
from time import sleep

from main import check_for_redirect, parse_book_page, save_text, download_image
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

ENCODING = 'UTF-8'
logger = logging.getLogger(__file__)


def create_json_file_with_books(books, dest_folder, json_path):
    if json_path:
        dest_folder = json_path
    file_path = os.path.join(dest_folder, 'books.json')
    with open(file_path, 'w') as file:
        json.dump(books, file, ensure_ascii=False)


def get_books(book_ids, skip_imgs, skip_txt, dest_folder):
    books = []
    url = 'https://tululu.org/'
    for book_id in tqdm(book_ids):
        params = {'id': book_id}
        try:
            response = requests.get(url=f'{url}txt.php',
                                    params=params, timeout=10)
            response.raise_for_status()
            check_for_redirect(response)
            html_book_page = requests.get(url=f'{url}b{book_id}/', timeout=10)
            html_book_page.raise_for_status()
            check_for_redirect(html_book_page)
            book = parse_book_page(html_book_page)
            if not skip_txt:
                book_file_path = save_text(
                    response,
                    str(book_id),
                    dest_folder,
                )
                book['book_path'] = book_file_path
            if not skip_imgs:
                img_link = urljoin(html_book_page.url, book.get('img_src'))
                img_file_path = download_image(img_link, book_id, dest_folder)
                book['img_src'] = img_file_path
        except requests.exceptions.HTTPError as http_er:
            logger.info(f'Невозможно загрузить книгу по данному '
                        f'book_id = {book_id}\n{http_er}\n')
            sys.stderr.write(f'{http_er}\n\n')
            continue
        except requests.exceptions.ConnectionError as connect_er:
            logger.warning(f'Произошёл сетевой сбой на книге с данным '
                           f'book_id = {book_id}\n{connect_er}\n')
            sys.stderr.write(f'{connect_er}\n\n')
            sleep(15)
            continue
        books.append(book)
        print(f'Название: {book.get("title")}')
        print(f'Автор: {book.get("author")}\n')
    return books


def get_book_ids(start_page, end_page):
    url = 'https://tululu.org/'
    book_ids = []
    for page_number in range(start_page, end_page):
        book_category = f'l55/{page_number}/'
        book_category_url = urljoin(url, book_category)
        try:
            response = requests.get(book_category_url)
            response.raise_for_status()
            check_for_redirect(response)
        except requests.exceptions.HTTPError as http_er:
            logger.warning(f'Невозможно загрузить страницу '
                           f'page_number = {page_number}\n{http_er}\n')
            sys.stderr.write(f'{http_er}\n\n')
            continue
        except requests.exceptions.ConnectionError as connect_er:
            logger.warning(f'Произошёл сетевой сбой на странице '
                           f'page_number = {page_number}\n{connect_er}\n')
            sys.stderr.write(f'{connect_er}\n\n')
            sleep(15)
            continue
        soup = BeautifulSoup(response.text, 'lxml')
        all_books_per_page = soup.select('body table.d_book')
        for book in all_books_per_page:
            book_href = book.select_one('a').get('href')
            book_id = int(re.search(r'\d+', book_href).group(0))
            book_ids.append(book_id)
    return book_ids


def main():
    logging.basicConfig(
        filename='app.log',
        filemode='w',
        level=logging.INFO,
        format='%(name)s - %(levelname)s - %(asctime)s - %(message)s'
    )
    logger.setLevel(logging.INFO)
    handler = RotatingFileHandler('app.log', maxBytes=15000, backupCount=2)
    logger.addHandler(handler)
    parser = argparse.ArgumentParser(
        description='Скачивает книги в указанном диапазоне'
    )
    parser.add_argument('--start_page', default=700, type=int,
                        help='Начало диапазона')
    parser.add_argument('--end_page', default=702, type=int,
                        help='Конец диапазона')
    parser.add_argument('--skip_imgs', action='store_true', default=False,
                        help='Нужно ли исключить скачивание обложек книг?')
    parser.add_argument('--skip_txt', action='store_true', default=False,
                        help='Нужно ли исключить скачивание текста книг?')
    parser.add_argument('--json_path', default='', type=str,
                        help='Путь к *.json файлу с результатами')
    parser.add_argument('--dest_folder', default='', type=str,
                        help='''Путь к каталогу с результатами \
                                парсинга: картинкам, книгам, JSON''')
    args = parser.parse_args()
    book_ids = get_book_ids(args.start_page, args.end_page)
    books = get_books(
        book_ids,
        args.skip_imgs,
        args.skip_txt,
        args.dest_folder
    )
    create_json_file_with_books(books, args.dest_folder, args.json_path)


if __name__ == '__main__':
    main()
