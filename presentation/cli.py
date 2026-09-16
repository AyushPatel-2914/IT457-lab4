"""Menu-driven CLI.

This tier only collects input, calls BookService, and formats the result. It
holds no business rules and never touches sqlite3 or any other storage library.
"""

from typing import List

from business.book_service import BookService
from business.errors import LibraryError
from business.models import Book

MENU = """
========== LIBRARY MANAGEMENT ==========
1. Add a book
2. View all books
3. Search books (title or author)
4. Update a book
5. Delete a book
6. Check out a book
0. Exit
========================================"""


class LibraryCLI:
    def __init__(self, service: BookService, backend_name: str = "SQLite"):
        self._service = service
        self._backend_name = backend_name

    def run(self) -> None:
        print(f"\nConnected to the {self._backend_name} data source.")
        actions = {
            "1": self._add_book,
            "2": self._view_books,
            "3": self._search_books,
            "4": self._update_book,
            "5": self._delete_book,
            "6": self._check_out_book,
        }
        while True:
            print(MENU)
            choice = input("Choose an option: ").strip()
            if choice == "0":
                print("Goodbye.")
                return
            action = actions.get(choice)
            if action is None:
                print("!! Unknown option. Pick a number from the menu.")
                continue
            try:
                action()
            except LibraryError as error:
                print(f"!! {error}")

    def _add_book(self) -> None:
        book = self._service.add_book(
            title=input("Title: "),
            author=input("Author: "),
            isbn=input("ISBN (10 or 13 digits): "),
            year=input("Publication year: "),
            quantity=input("Quantity: "),
        )
        print(f"Added '{book.title}' with id {book.id}.")

    def _view_books(self) -> None:
        self._print_table(self._service.list_books())

    def _search_books(self) -> None:
        results = self._service.search_books(input("Search term: "))
        if not results:
            print("No matching books.")
            return
        self._print_table(results)

    def _update_book(self) -> None:
        book_id = input("Id of the book to update: ")
        current = self._service.get_book(book_id)
        print(f"Editing '{current.title}'. Press Enter to keep a field unchanged.")
        fields = {
            "title": self._optional(f"Title [{current.title}]: "),
            "author": self._optional(f"Author [{current.author}]: "),
            "isbn": self._optional(f"ISBN [{current.isbn}]: "),
            "year": self._optional(f"Year [{current.year}]: "),
            "quantity": self._optional(f"Quantity [{current.quantity}]: "),
        }
        updated = self._service.update_book(book_id, **fields)
        print(f"Updated book {updated.id}.")

    def _delete_book(self) -> None:
        book_id = input("Id of the book to delete: ")
        self._service.delete_book(book_id)
        print(f"Deleted book {book_id}.")

    def _check_out_book(self) -> None:
        book = self._service.check_out_book(input("Id of the book to check out: "))
        print(f"Checked out '{book.title}'. {book.quantity} copies left.")

    @staticmethod
    def _optional(prompt: str):
        value = input(prompt).strip()
        return value or None

    @staticmethod
    def _print_table(books: List[Book]) -> None:
        if not books:
            print("The collection is empty.")
            return
        header = f"{'ID':<4} {'TITLE':<30} {'AUTHOR':<22} {'ISBN':<15} {'YEAR':<6} {'QTY':<4}"
        print(header)
        print("-" * len(header))
        for book in books:
            print(
                f"{book.id:<4} {book.title[:30]:<30} {book.author[:22]:<22} "
                f"{book.isbn:<15} {book.year:<6} {book.quantity:<4}"
            )
