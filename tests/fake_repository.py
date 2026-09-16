"""A fake data source used by the unit tests.

It implements BookRepository with a dictionary, so the business tests never
touch SQLite or any file on disk. It also records which methods were called,
which lets a test assert that the business tier stopped before writing.
"""

from dataclasses import replace
from typing import List, Optional

from business.models import Book
from business.repository import BookRepository


class FakeBookRepository(BookRepository):
    def __init__(self, books: Optional[List[Book]] = None):
        self._books = {}
        self._next_id = 1
        self.calls = []
        for book in books or []:
            self.add(book)
        self.calls.clear()

    def add(self, book: Book) -> Book:
        self.calls.append("add")
        stored = replace(book, id=book.id or self._next_id)
        self._next_id = max(self._next_id, stored.id) + 1
        self._books[stored.id] = stored
        return replace(stored)

    def get_all(self) -> List[Book]:
        self.calls.append("get_all")
        return [replace(b) for b in self._books.values()]

    def get_by_id(self, book_id: int) -> Optional[Book]:
        self.calls.append("get_by_id")
        book = self._books.get(book_id)
        return replace(book) if book else None

    def find_by_isbn(self, isbn: str) -> Optional[Book]:
        self.calls.append("find_by_isbn")
        for book in self._books.values():
            if book.isbn == isbn:
                return replace(book)
        return None

    def search(self, term: str) -> List[Book]:
        self.calls.append("search")
        needle = term.lower()
        return [
            replace(b)
            for b in self._books.values()
            if needle in b.title.lower() or needle in b.author.lower()
        ]

    def update(self, book: Book) -> Book:
        self.calls.append("update")
        self._books[book.id] = replace(book)
        return replace(book)

    def delete(self, book_id: int) -> bool:
        self.calls.append("delete")
        return self._books.pop(book_id, None) is not None
