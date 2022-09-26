from pathlib import Path
import os
from urllib.parse import urljoin, urlsplit
from pprint import pprint

import requests
import requests.exceptions
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename


ENCODING = 'UTF-8'


def check_for_redirect(response):
    if response.history:
        raise requests.exceptions.HTTPError('Неверный тип данных')


def parse_book_page(url):
    response = requests.get(url)
    response.raise_for_status()
    book_data = {}
    soup = BeautifulSoup(response.text, 'lxml')
    title_and_author = soup.find('body').find('h1')
    title, author = title_and_author.text.split('::')
    book_data['Название'] = sanitize_filename(title).strip()
    book_data['Автор'] = sanitize_filename(author).strip()
    comments_blog = soup.find_all(class_='texts')
    comments = ''
    for comment in comments_blog:
        comments += f'{comment.span.string}\n'
    book_data['Комментарии'] = comments
    book_genres = soup.find('span', class_='d_book').find_all('a')
    genres = []
    for genre in book_genres:
        genres.append(genre.text)
    book_data['Жанры'] = genres
    img_src = soup.find(class_='bookimage').find('img')['src']
    pprint(book_data)
    return (title, author, img_src)


def get_file_extension(url):
    parsed_url = urlsplit(url)
    filename = os.path.split(parsed_url.path)[1]
    return os.path.splitext(filename)[1]


def download_image(img_link, id, folder='images'):
    Path(folder).mkdir(parents=True, exist_ok=True)
    response = requests.get(img_link)
    response.raise_for_status()
    if img_link.endswith('nopic.gif'):
        img_name = 'nopic.gif'
    else:
        extension = get_file_extension(img_link)
        img_name = f'{id}.{extension}'
    with open(os.path.join(folder, img_name), 'wb') as file:
        file.write(response.content)


def save_text(response, filename, folder='books'):
    Path(folder).mkdir(parents=True, exist_ok=True)
    filename = sanitize_filename(filename).strip()
    with open(os.path.join(folder, f'{filename}.txt'),
              'w', encoding=ENCODING) as file:
        file.write(response.text)


def main():
    for id in range(1, 11):
        params = {'id': id}
        url = 'https://tululu.org/'
        try:
            response = requests.get(f'{url}txt.php', params=params)
            response.raise_for_status()
            check_for_redirect(response)
        except requests.exceptions.HTTPError:
            continue
        title, author, img_src = parse_book_page(f'{url}b{id}')
        save_text(response, f'{id}. {title}')
        img_link = urljoin(url, img_src)
        download_image(img_link, id)


if __name__ == '__main__':
    main()
