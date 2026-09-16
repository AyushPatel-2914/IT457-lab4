"""Storage implementation backed by a plain Python list."""

from dataclasses import replace
from typing import List, Optional

from business.models import Book
from business.repository import BookRepository


class InMemoryBookRepository(BookRepository):
    def __init__(self):
        self._books: List[Book] = []
        self._next_id = 1

    def add(self, book: Book) -> Book:
        stored = replace(book, id=self._next_id)
        self._next_id += 1
        self._books.append(stored)
        return replace(stored)

    def get_all(self) -> List[Book]:
        return [replace(b) for b in self._books]

    def get_by_id(self, book_id: int) -> Optional[Book]:
        for book in self._books:
            if book.id == book_id:
                return replace(book)
        return None

    def find_by_isbn(self, isbn: str) -> Optional[Book]:
        for book in self._books:
            if book.isbn == isbn:
                return replace(book)
        return None

    def search(self, term: str) -> List[Book]:
        needle = term.lower()
        return [
            replace(b)
            for b in self._books
            if needle in b.title.lower() or needle in b.author.lower()
        ]

    def update(self, book: Book) -> Book:
        for index, stored in enumerate(self._books):
            if stored.id == book.id:
                self._books[index] = replace(book)
                return replace(book)
        return book

    def delete(self, book_id: int) -> bool:
        for index, stored in enumerate(self._books):
            if stored.id == book_id:
                del self._books[index]
                return True
        return False
