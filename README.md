# Парсер книг с сайта [tululu.org](https://tululu.org/)
Проект позволяет скачивать книги с сайта [tululu.org](https://tululu.org/). В папке `books/` будут сохраняться книги, а в папке `images/` обложки данных книг.

## Как установить
Для запуска проекта потребуется Python3. Также для его работы необходимы сторонние библиотеки, установим их с файла `requirements.txt`
```
pip install -r requirements.txt 
```
## Аргументы
Для скачивания книг нужно в момент запуска обязательно указать аргументы. В данном проекте агрументы нужны для выбора диапазона, в котором будут скачиваться книги.
## Запуск
Основной код написан в файле `main.py`. Во время запуска не забываем про агрументы, например:
```
python main.py 10 20
```