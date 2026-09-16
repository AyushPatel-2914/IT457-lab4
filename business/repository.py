"""The storage abstraction the business tier depends on.

The business tier never imports sqlite3 or any other storage library. It only
knows this interface, so any class in the data tier that implements it can be
plugged in without changing a line of business code.
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from business.models import Book


class BookRepository(ABC):
    @abstractmethod
    def add(self, book: Book) -> Book:
        """Persist a new book and return it with its assigned id."""

    @abstractmethod
    def get_all(self) -> List[Book]:
        """Return every stored book."""

    @abstractmethod
    def get_by_id(self, book_id: int) -> Optional[Book]:
        """Return the book with this id, or None."""

    @abstractmethod
    def find_by_isbn(self, isbn: str) -> Optional[Book]:
        """Return the book with this ISBN, or None."""

    @abstractmethod
    def search(self, term: str) -> List[Book]:
        """Return books whose title or author contains term (case-insensitive)."""

    @abstractmethod
    def update(self, book: Book) -> Book:
        """Overwrite the stored book that has book.id."""

    @abstractmethod
    def delete(self, book_id: int) -> bool:
        """Remove the book with this id. Return True if something was removed."""
