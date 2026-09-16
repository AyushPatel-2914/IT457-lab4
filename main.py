"""Composition root: the only place where a concrete data source is chosen."""

import argparse

from business.book_service import BookService
from data.in_memory_repository import InMemoryBookRepository
from data.sqlite_repository import SQLiteBookRepository
from presentation.cli import LibraryCLI


def build_repository(store: str, db_path: str):
    if store == "memory":
        return InMemoryBookRepository(), "in-memory list"
    return SQLiteBookRepository(db_path), f"SQLite ({db_path})"


def main() -> None:
    parser = argparse.ArgumentParser(description="Library Management System")
    parser.add_argument(
        "--ui",
        choices=["cli", "web"],
        default="cli",
        help="which presentation tier to start",
    )
    parser.add_argument(
        "--store",
        choices=["sqlite", "memory"],
        default="sqlite",
        help="which data-tier implementation to run against",
    )
    parser.add_argument("--db", default="library.db", help="SQLite database file")
    parser.add_argument("--port", type=int, default=5000, help="port for --ui web")
    args = parser.parse_args()

    repository, backend_name = build_repository(args.store, args.db)
    service = BookService(repository)

    if args.ui == "web":
        from presentation.web_app import create_app

        print(f"Serving the web UI on http://127.0.0.1:{args.port}  (Ctrl+C to stop)")
        create_app(service, backend_name).run(port=args.port, debug=False)
    else:
        LibraryCLI(service, backend_name).run()


if __name__ == "__main__":
    main()
