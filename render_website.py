import os
import json
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

from more_itertools import chunked
from livereload import Server
from jinja2 import Environment, FileSystemLoader, select_autoescape

html_pages_folder = 'pages'

env = Environment(
    loader=FileSystemLoader('.'),
    autoescape=select_autoescape(['html', 'xml'])
)

def rebuild():
    template = env.get_template('template.html')
    Path(html_pages_folder).mkdir(parents=True, exist_ok=True)
    with open('books.json', 'r') as file:
        books = json.load(file)

    book_pages = list(chunked(books, 20))
    for number, book_page in enumerate(book_pages, 1):
        books = list(chunked(book_page, len(book_page) // 2))
        rendered_page = template.render(books=book_page)
        filepath = os.path.join(html_pages_folder, f'index{number}.html')
        with open(filepath, 'w', encoding="utf8") as file:
            file.write(rendered_page)
    print("Site rebuilt")


rebuild()
server = Server()
server.watch('template.html', rebuild)
server.serve(root='.', host='127.0.0.1', port=5500)
