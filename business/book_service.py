"""Orchestration for every Book use case.

Every rule lives here. The presentation tier calls these methods and the data
tier is reached only through the BookRepository abstraction.
"""

from typing import List, Optional

from business.errors import (
    BookNotFoundError,
    DuplicateISBNError,
    OutOfStockError,
    ValidationError,
)
from business.models import Book
from business.repository import BookRepository
from business.validators import (
    validate_author,
    validate_isbn,
    validate_quantity,
    validate_title,
    validate_year,
)


class BookService:
    def __init__(self, repository: BookRepository):
        self._repo = repository

    def add_book(self, title, author, isbn, year, quantity) -> Book:
        book = Book(
            title=validate_title(title),
            author=validate_author(author),
            isbn=validate_isbn(isbn),
            year=validate_year(year),
            quantity=validate_quantity(quantity),
        )
        existing = self._repo.find_by_isbn(book.isbn)
        if existing is not None:
            raise DuplicateISBNError(
                f"A book with ISBN {book.isbn} already exists (id {existing.id})."
            )
        return self._repo.add(book)

    def list_books(self) -> List[Book]:
        return self._repo.get_all()

    def get_book(self, book_id: int) -> Book:
        book = self._repo.get_by_id(self._coerce_id(book_id))
        if book is None:
            raise BookNotFoundError(f"No book found with id {book_id}.")
        return book

    def search_books(self, term) -> List[Book]:
        if not isinstance(term, str) or not term.strip():
            raise ValidationError("Search term cannot be empty.")
        return self._repo.search(term.strip())

    def update_book(
        self,
        book_id: int,
        title=None,
        author=None,
        isbn=None,
        year=None,
        quantity=None,
    ) -> Book:
        book = self.get_book(book_id)

        if title is not None:
            book.title = validate_title(title)
        if author is not None:
            book.author = validate_author(author)
        if isbn is not None:
            new_isbn = validate_isbn(isbn)
            clash = self._repo.find_by_isbn(new_isbn)
            if clash is not None and clash.id != book.id:
                raise DuplicateISBNError(
                    f"A book with ISBN {new_isbn} already exists (id {clash.id})."
                )
            book.isbn = new_isbn
        if year is not None:
            book.year = validate_year(year)
        if quantity is not None:
            book.quantity = validate_quantity(quantity)

        return self._repo.update(book)

    def delete_book(self, book_id: int) -> None:
        if not self._repo.delete(self._coerce_id(book_id)):
            raise BookNotFoundError(f"No book found with id {book_id}.")

    def check_out_book(self, book_id: int) -> Book:
        book = self.get_book(book_id)
        if book.quantity <= 0:
            raise OutOfStockError(
                f"'{book.title}' is out of stock and cannot be checked out."
            )
        book.quantity -= 1
        return self._repo.update(book)

    @staticmethod
    def _coerce_id(book_id) -> int:
        try:
            return int(book_id)
        except (TypeError, ValueError):
            raise ValidationError("Book id must be a whole number.")
