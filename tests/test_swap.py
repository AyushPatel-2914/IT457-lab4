"""Runs the swap scenario as a test so `python -m unittest` covers it too."""

import os
import tempfile
import unittest

from business.book_service import BookService
from data.in_memory_repository import InMemoryBookRepository
from data.sqlite_repository import SQLiteBookRepository
from swap_test import run_scenario


class TestDataLayerSwap(unittest.TestCase):
    def test_both_repositories_produce_identical_results(self):
        memory_result = run_scenario(BookService(InMemoryBookRepository()))

        db_path = os.path.join(tempfile.mkdtemp(), "swap_test.db")
        repo = SQLiteBookRepository(db_path)
        try:
            sqlite_result = run_scenario(BookService(repo))
        finally:
            repo.close()

        self.assertEqual(memory_result, sqlite_result)


if __name__ == "__main__":
    unittest.main()
