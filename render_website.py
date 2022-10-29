import os
import json
from pathlib import Path

from more_itertools import chunked
from jinja2 import Environment, FileSystemLoader, select_autoescape

ENCODING = 'UTF-8'


def create_offline_website(env, html_pages_folder, books_number_per_page):
    template = env.get_template('template.html')
    with open('books.json', 'r') as file:
        books = json.load(file)
    book_pages = list(chunked(books, books_number_per_page))
    pages_number = len(book_pages)

    for number, book_page in enumerate(book_pages, 1):
        books_per_page = list(chunked(book_page, len(book_page) // 2))
        rendered_page = template.render(
            books=books_per_page,
            pages_number=pages_number,
            current_page=number
        )
        filepath = os.path.join(html_pages_folder, f'index{number}.html')
        with open(filepath, 'w', encoding=ENCODING) as file:
            file.write(rendered_page)


def main():
    html_pages_folder = 'pages'
    books_number_per_page = 20
    Path(html_pages_folder).mkdir(parents=True, exist_ok=True)
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    create_offline_website(env, html_pages_folder, books_number_per_page)
    print('Сайт библиотеки создан')

if __name__ == '__main__':
    main()
