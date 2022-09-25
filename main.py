from pathlib import Path
import os

import requests

Path('books').mkdir(parents=True, exist_ok=True)


def fetch_books():
    book_id = 32160
    for id in range(book_id, book_id + 20):
        params = {'id': id}
        url = 'https://tululu.org/txt.php'
        response = requests.get(url, params=params)
        response.raise_for_status()
        if response.text.startswith('<!DOCTYPE'):
            continue
        with open(os.path.join('books', f'book_{id}.txt'), 'w') as file:
            file.write(response.text)


fetch_books()
