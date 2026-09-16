"""Swap test: the same business scenario, run against two different data layers.

The scenario below only ever talks to BookService. Nothing in /business changes
between the two runs -- only the repository handed to the service at startup.
"""

import os
import tempfile

from business.book_service import BookService
from business.errors import OutOfStockError, ValidationError
from data.in_memory_repository import InMemoryBookRepository
from data.sqlite_repository import SQLiteBookRepository


def run_scenario(service: BookService) -> list:
    """Exercise every feature and return a transcript of the outcomes."""
    transcript = []

    dune = service.add_book("Dune", "Frank Herbert", "0441013597", 1965, 1)
    service.add_book("Neuromancer", "William Gibson", "0441569595", 1984, 4)
    service.add_book("Dune Messiah", "Frank Herbert", "0441172695", 1969, 2)
    transcript.append(("count after adds", len(service.list_books())))

    transcript.append(
        ("search 'dune'", sorted(b.title for b in service.search_books("dune")))
    )
    transcript.append(
        ("search 'gibson'", sorted(b.title for b in service.search_books("gibson")))
    )

    updated = service.update_book(dune.id, title="Dune (Deluxe Edition)", quantity=1)
    transcript.append(("updated title", updated.title))

    checked_out = service.check_out_book(dune.id)
    transcript.append(("quantity after checkout", checked_out.quantity))

    try:
        service.check_out_book(dune.id)
        transcript.append(("checkout at zero", "NO ERROR -- BUG"))
    except OutOfStockError:
        transcript.append(("checkout at zero", "OutOfStockError"))

    try:
        service.add_book("", "Nobody", "123", 3000, -1)
        transcript.append(("invalid book", "NO ERROR -- BUG"))
    except ValidationError:
        transcript.append(("invalid book", "ValidationError"))

    service.delete_book(dune.id)
    transcript.append(("count after delete", len(service.list_books())))
    transcript.append(
        ("remaining titles", sorted(b.title for b in service.list_books()))
    )
    return transcript


def main() -> int:
    memory_result = run_scenario(BookService(InMemoryBookRepository()))

    db_path = os.path.join(tempfile.mkdtemp(), "swap_test.db")
    sqlite_repo = SQLiteBookRepository(db_path)
    sqlite_result = run_scenario(BookService(sqlite_repo))
    sqlite_repo.close()

    print(f"{'STEP':<26} {'IN-MEMORY':<40} {'SQLITE':<40}")
    print("-" * 108)
    for (step, memory_value), (_, sqlite_value) in zip(memory_result, sqlite_result):
        print(f"{step:<26} {str(memory_value):<40} {str(sqlite_value):<40}")

    print()
    if memory_result == sqlite_result:
        print("PASS: both data layers produced identical results.")
        print("The business tier was not modified between the two runs.")
        return 0
    print("FAIL: the two data layers disagreed.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
