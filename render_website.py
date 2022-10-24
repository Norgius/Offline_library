import json
from http.server import HTTPServer, SimpleHTTPRequestHandler

from livereload import Server
from jinja2 import Environment, FileSystemLoader, select_autoescape

env = Environment(
    loader=FileSystemLoader('.'),
    autoescape=select_autoescape(['html', 'xml'])
)

def rebuild():
    template = env.get_template('template.html')
    with open('books.json', 'r') as file:
        books = json.load(file)
    rendered_page = template.render(books=books)
    with open('index.html', 'w', encoding="utf8") as file:
        file.write(rendered_page)
    print("Site rebuilt")


rebuild()
server = Server()
server.watch('template.html', rebuild)
server.serve(root='.', host='127.0.0.1', port=5500)
