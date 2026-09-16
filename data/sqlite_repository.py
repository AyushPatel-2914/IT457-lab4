"""Storage implementation backed by SQLite."""

import sqlite3
from typing import List, Optional

from business.models import Book
from business.repository import BookRepository

SCHEMA = """
CREATE TABLE IF NOT EXISTS books (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    title    TEXT    NOT NULL,
    author   TEXT    NOT NULL,
    isbn     TEXT    NOT NULL,
    year     INTEGER NOT NULL,
    quantity INTEGER NOT NULL
)
"""


class SQLiteBookRepository(BookRepository):
    def __init__(self, db_path: str = "library.db"):
        # check_same_thread=False so the same connection can serve Flask's
        # worker threads; this app has a single user, so writes never overlap.
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute(SCHEMA)
        self._conn.commit()

    def close(self) -> None:
        self._conn.close()

    def add(self, book: Book) -> Book:
        cursor = self._conn.execute(
            "INSERT INTO books (title, author, isbn, year, quantity) VALUES (?, ?, ?, ?, ?)",
            (book.title, book.author, book.isbn, book.year, book.quantity),
        )
        self._conn.commit()
        return Book(
            id=cursor.lastrowid,
            title=book.title,
            author=book.author,
            isbn=book.isbn,
            year=book.year,
            quantity=book.quantity,
        )

    def get_all(self) -> List[Book]:
        rows = self._conn.execute("SELECT * FROM books ORDER BY id").fetchall()
        return [self._to_book(row) for row in rows]

    def get_by_id(self, book_id: int) -> Optional[Book]:
        row = self._conn.execute(
            "SELECT * FROM books WHERE id = ?", (book_id,)
        ).fetchone()
        return self._to_book(row) if row else None

    def find_by_isbn(self, isbn: str) -> Optional[Book]:
        row = self._conn.execute(
            "SELECT * FROM books WHERE isbn = ?", (isbn,)
        ).fetchone()
        return self._to_book(row) if row else None

    def search(self, term: str) -> List[Book]:
        pattern = f"%{term}%"
        rows = self._conn.execute(
            "SELECT * FROM books WHERE title LIKE ? OR author LIKE ? ORDER BY id",
            (pattern, pattern),
        ).fetchall()
        return [self._to_book(row) for row in rows]

    def update(self, book: Book) -> Book:
        self._conn.execute(
            "UPDATE books SET title = ?, author = ?, isbn = ?, year = ?, quantity = ? WHERE id = ?",
            (book.title, book.author, book.isbn, book.year, book.quantity, book.id),
        )
        self._conn.commit()
        return book

    def delete(self, book_id: int) -> bool:
        cursor = self._conn.execute("DELETE FROM books WHERE id = ?", (book_id,))
        self._conn.commit()
        return cursor.rowcount > 0

    @staticmethod
    def _to_book(row: sqlite3.Row) -> Book:
        return Book(
            id=row["id"],
            title=row["title"],
            author=row["author"],
            isbn=row["isbn"],
            year=row["year"],
            quantity=row["quantity"],
        )
