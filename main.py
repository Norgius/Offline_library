from pathlib import Path
import os
from urllib.parse import urljoin, urlsplit

import requests
import requests.exceptions
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename


ENCODING = 'UTF-8'


def check_for_redirect(response):
    if response.history:
        raise requests.exceptions.HTTPError('Неверный тип данных')


def parse_book_page(html_book_page):
    book_data = {}
    soup = BeautifulSoup(html_book_page.text, 'lxml')
    title_and_author = soup.find('body').find('h1')
    title, author = title_and_author.text.split('::')
    title = sanitize_filename(title).strip()
    author = sanitize_filename(author).strip()
    comments_blog = soup.find_all(class_='texts')
    comments = []
    for comment in comments_blog:
        comments.append(f'{comment.span.string}')
    book_genres = soup.find('span', class_='d_book').find_all('a')
    genres = []
    for genre in book_genres:
        genres.append(genre.text)
    img_src = soup.find(class_='bookimage').find('img')['src']
    book_data['Название'] = title
    book_data['Автор'] = author
    book_data['Комментарии'] = comments
    book_data['Жанры'] = genres
    return (title, img_src, book_data)


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
            response = requests.get(url=f'{url}txt.php', params=params)
            response.raise_for_status()
            check_for_redirect(response)
        except requests.exceptions.HTTPError:
            continue
        html_book_page = requests.get(url=f'{url}b{id}')
        html_book_page.raise_for_status()
        title, img_src, book_data = parse_book_page(html_book_page)
        save_text(response, filename=f'{id}. {title}')
        img_link = urljoin(url, img_src)
        download_image(img_link, id)


if __name__ == '__main__':
    main()
