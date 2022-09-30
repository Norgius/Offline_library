from pathlib import Path
import sys
from urllib.parse import urljoin, urlsplit
import argparse
import os
import logging
from logging.handlers import RotatingFileHandler

import requests
import requests.exceptions
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename

ENCODING = 'UTF-8'

logger = logging.getLogger(__file__)


def check_for_redirect(response):
    if response.history:
        raise requests.exceptions.HTTPError(
            f'Cо страницы - {response.history[0].url}\n'
            f'произошёл редирект на страницу - {response.url}'
        )


def parse_book_page(html_book_page):
    soup = BeautifulSoup(html_book_page.text, 'lxml')
    title_and_author = soup.find('body').find('h1')
    title, author = title_and_author.text.split('::')
    title = sanitize_filename(title).strip()
    author = sanitize_filename(author).strip()
    comments_blog = soup.find_all(class_='texts')
    comments = [comment.span.string for comment in comments_blog]
    book_genres = soup.find('span', class_='d_book').find_all('a')
    genres = [genre.text for genre in book_genres]
    img_src = soup.find(class_='bookimage').find('img')['src']
    book = {'title': title, 'author': author, 'comments': comments,
            'genres': genres, 'img_src': img_src}
    return book


def get_file_extension(url):
    parsed_url = urlsplit(url)
    filename = os.path.split(parsed_url.path)[1]
    return os.path.splitext(filename)[1]


def download_image(img_link, book_id, folder='images'):
    Path(folder).mkdir(parents=True, exist_ok=True)
    response = requests.get(img_link)
    response.raise_for_status()
    if img_link.endswith('nopic.gif'):
        img_name = 'nopic.gif'
    else:
        extension = get_file_extension(img_link)
        img_name = f'{book_id}.{extension}'
    file_path = os.path.join(folder, img_name)
    with open(file_path, 'wb') as file:
        file.write(response.content)


def save_text(response, filename, folder='books'):
    Path(folder).mkdir(parents=True, exist_ok=True)
    filename = sanitize_filename(filename).strip()
    file_path = os.path.join(folder, f'{filename}.txt')
    with open(file_path, 'w', encoding=ENCODING) as file:
        file.write(response.text)


def work_with_books(start_id, end_id):
    for book_id in range(start_id, end_id):
        url = 'https://tululu.org/'
        params = {'id': book_id}
        try:
            response = requests.get(url=f'{url}txt.php',
                                    params=params, timeout=10)
            response.raise_for_status()
            check_for_redirect(response)
            html_book_page = requests.get(url=f'{url}b{book_id}/', timeout=10)
            html_book_page.raise_for_status()
            check_for_redirect(html_book_page)
        except requests.exceptions.HTTPError as http_er:
            logger.info(f'Невозможно загрузить книгу по данному '
                        f'book_id = {book_id}\n{http_er}\n')
            sys.stderr.write(f'{http_er}\n\n')
            continue
        except requests.exceptions.ConnectionError as connect_er:
            logger.warning(f'Произошёл сетевой сбой на книге с данным '
                           f'book_id = {book_id}\n{connect_er}\n')
            sys.stderr.write(f'{connect_er}\n\n')
            continue
        book = parse_book_page(html_book_page)
        save_text(response, filename=f'{book_id}. {book.get("title")}')
        img_link = urljoin(html_book_page.url, book.get('img_src'))
        download_image(img_link, book_id)

        print(f'Название: {book.get("title")}')
        print(f'Автор: {book.get("author")}\n')


def main():
    logging.basicConfig(filename='app.log', filemode='w', level=logging.INFO,
                        format='%(name)s - %(levelname)s '
                               '- %(asctime)s - %(message)s')
    logger.setLevel(logging.INFO)
    handler = RotatingFileHandler('app.log', maxBytes=3000, backupCount=2)
    logger.addHandler(handler)
    parser = argparse.ArgumentParser(
        description='Скачивает книги в указанном диапазоне'
    )
    parser.add_argument('start_id', type=int,
                        help='Начало диапазона')
    parser.add_argument('end_id', type=int,
                        help='Конец диапазона')
    args = parser.parse_args()
    work_with_books(args.start_id, args.end_id)


if __name__ == '__main__':
    main()
