"""Unit tests for the business tier. Every test runs against FakeBookRepository."""

import unittest
from datetime import date

from business.book_service import BookService
from business.errors import (
    BookNotFoundError,
    DuplicateISBNError,
    OutOfStockError,
    ValidationError,
)
from business.models import Book
from tests.fake_repository import FakeBookRepository


def sample_books():
    return [
        Book(title="Dune", author="Frank Herbert", isbn="0441013597", year=1965, quantity=3),
        Book(title="Neuromancer", author="William Gibson", isbn="0441569595", year=1984, quantity=0),
        Book(title="Dune Messiah", author="Frank Herbert", isbn="0441172695", year=1969, quantity=1),
    ]


class BookServiceTestCase(unittest.TestCase):
    def setUp(self):
        self.repo = FakeBookRepository(sample_books())
        self.service = BookService(self.repo)


class TestAddBook(BookServiceTestCase):
    def test_adds_valid_book_and_assigns_id(self):
        book = self.service.add_book("Snow Crash", "Neal Stephenson", "0553380958", 1992, 2)
        self.assertIsNotNone(book.id)
        self.assertEqual(book.title, "Snow Crash")
        self.assertEqual(len(self.service.list_books()), 4)

    def test_trims_whitespace_and_strips_isbn_hyphens(self):
        book = self.service.add_book("  Hyperion  ", " Dan Simmons ", "978-0-553-28368-6", 1989, 1)
        self.assertEqual(book.title, "Hyperion")
        self.assertEqual(book.author, "Dan Simmons")
        self.assertEqual(book.isbn, "9780553283686")

    def test_empty_title_is_rejected(self):
        with self.assertRaises(ValidationError):
            self.service.add_book("   ", "Someone", "0441013597", 2000, 1)

    def test_empty_author_is_rejected(self):
        with self.assertRaises(ValidationError):
            self.service.add_book("A Title", "", "1234567890", 2000, 1)

    def test_isbn_must_be_10_or_13_digits(self):
        for bad_isbn in ["12345", "12345678901", "abcdefghij", ""]:
            with self.subTest(isbn=bad_isbn):
                with self.assertRaises(ValidationError):
                    self.service.add_book("A Title", "An Author", bad_isbn, 2000, 1)

    def test_future_publication_year_is_rejected(self):
        with self.assertRaises(ValidationError):
            self.service.add_book("A Title", "An Author", "1234567890", date.today().year + 1, 1)

    def test_negative_quantity_is_rejected(self):
        with self.assertRaises(ValidationError):
            self.service.add_book("A Title", "An Author", "1234567890", 2000, -1)

    def test_duplicate_isbn_is_rejected(self):
        with self.assertRaises(DuplicateISBNError):
            self.service.add_book("Dune Reprint", "Frank Herbert", "0441013597", 1965, 1)

    def test_invalid_book_is_never_written_to_the_data_layer(self):
        self.repo.calls.clear()
        with self.assertRaises(ValidationError):
            self.service.add_book("", "An Author", "1234567890", 2000, 1)
        self.assertNotIn("add", self.repo.calls)


class TestSearchAndRead(BookServiceTestCase):
    def test_list_returns_every_book(self):
        self.assertEqual(len(self.service.list_books()), 3)

    def test_search_matches_partial_title_case_insensitively(self):
        results = self.service.search_books("dune")
        self.assertEqual({b.title for b in results}, {"Dune", "Dune Messiah"})

    def test_search_matches_partial_author(self):
        results = self.service.search_books("herbert")
        self.assertEqual(len(results), 2)

    def test_empty_search_term_is_rejected(self):
        with self.assertRaises(ValidationError):
            self.service.search_books("  ")

    def test_get_unknown_id_raises_not_found(self):
        with self.assertRaises(BookNotFoundError):
            self.service.get_book(999)


class TestUpdateAndDelete(BookServiceTestCase):
    def test_update_changes_only_the_given_fields(self):
        updated = self.service.update_book(1, title="Dune (Revised)", quantity=7)
        self.assertEqual(updated.title, "Dune (Revised)")
        self.assertEqual(updated.quantity, 7)
        self.assertEqual(updated.author, "Frank Herbert")

    def test_update_rejects_invalid_values(self):
        with self.assertRaises(ValidationError):
            self.service.update_book(1, quantity=-5)

    def test_update_rejects_an_isbn_owned_by_another_book(self):
        with self.assertRaises(DuplicateISBNError):
            self.service.update_book(1, isbn="0441569595")

    def test_update_unknown_id_raises_not_found(self):
        with self.assertRaises(BookNotFoundError):
            self.service.update_book(999, title="Nothing")

    def test_delete_removes_the_book(self):
        self.service.delete_book(1)
        self.assertEqual(len(self.service.list_books()), 2)

    def test_delete_unknown_id_raises_not_found(self):
        with self.assertRaises(BookNotFoundError):
            self.service.delete_book(999)


class TestCheckOut(BookServiceTestCase):
    def test_checkout_decreases_quantity_by_one(self):
        book = self.service.check_out_book(1)
        self.assertEqual(book.quantity, 2)
        self.assertEqual(self.service.get_book(1).quantity, 2)

    def test_checkout_at_zero_raises_a_meaningful_error(self):
        with self.assertRaises(OutOfStockError) as ctx:
            self.service.check_out_book(2)
        self.assertIn("out of stock", str(ctx.exception).lower())

    def test_quantity_never_goes_below_zero(self):
        self.service.check_out_book(3)
        self.assertEqual(self.service.get_book(3).quantity, 0)
        with self.assertRaises(OutOfStockError):
            self.service.check_out_book(3)
        self.assertEqual(self.service.get_book(3).quantity, 0)

    def test_checkout_unknown_id_raises_not_found(self):
        with self.assertRaises(BookNotFoundError):
            self.service.check_out_book(999)


if __name__ == "__main__":
    unittest.main()
