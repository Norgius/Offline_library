from pprint import pprint
from urllib.parse import urljoin
import re
import logging
import sys
from time import sleep
import json

from main import check_for_redirect, parse_book_page, save_text, download_image
import requests
from bs4 import BeautifulSoup

ENCODING = 'UTF-8'
logger = logging.getLogger(__file__)


def create_json_file_with_books(books):
    books_json = json.dumps(books, ensure_ascii=False)
    with open('books.json', 'w') as file:
        file.write(books_json)


def get_books(url, book_ids):
    books = []
    for book_id in book_ids:
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
            book_file_path = save_text(response, filename=f'{book_id}. {book.get("title")}')
            img_link = urljoin(html_book_page.url, book.get('img_src'))
            img_file_path = download_image(img_link, book_id)
            book['book_path'] = book_file_path
            book['img_src'] = img_file_path
            books.append(book)
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
    return books


def get_book_ids():
    url = 'https://tululu.org/'
    book_ids = []
    for page_number in range(1, 5):
        book_category = f'l55/{page_number}/'
        book_category_url = urljoin(url, book_category)
        try:
            response = requests.get(book_category_url)
            response.raise_for_status()
            print(book_category_url)
        except requests.exceptions.HTTPError as http_er:
            logger.warning(f'Невозможно загрузить страницу '
                        f'page_number = {page_number}\n{http_er}\n')
            sys.stderr.write(f'{http_er}\n\n')
            sleep(15)
            continue
        except requests.exceptions.ConnectionError as connect_er:
            logger.warning(f'Произошёл сетевой сбой на странице '
                        f'page_number = {page_number}\n{connect_er}\n')
            sys.stderr.write(f'{connect_er}\n\n')
            sleep(15)
            continue
        soup = BeautifulSoup(response.text, 'lxml')
        all_books_per_page = soup.find('body').find_all(class_='d_book')
        for book in all_books_per_page:
            book_href = book.find('a').get('href')
            book_id = int(re.search(r'\d+', book_href).group(0))
            book_ids.append(book_id)
    books = get_books(url, book_ids)
    create_json_file_with_books(books)

get_book_ids()