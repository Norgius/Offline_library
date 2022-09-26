from pathlib import Path
import os

import requests
import requests.exceptions
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename


Path('books').mkdir(parents=True, exist_ok=True)
ENCODING = 'UTF-8'


def check_for_redirect(response):
    if response.history:
        raise requests.exceptions.HTTPError('Неверный тип данных')


def get_title_and_author(url):
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')
    title_tag = soup.find('body').find('h1')
    title, author = title_tag.text.split('::')
    return (title, author)


def download_txt(url, params, filename, folder='books'):
    response = requests.get(url, params=params)
    response.raise_for_status()
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
        title, author = get_title_and_author(f'{url}b{id}')
        download_txt(f'{url}txt.php', params, f'{id}. {title}')


if __name__ == '__main__':
    main()
