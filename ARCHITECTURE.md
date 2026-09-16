# Architecture Diagram — Library Management System

## The three tiers

```
                        +-----------------------------------------+
                        |          PRESENTATION TIER              |
                        |             /presentation               |
                        |                                         |
   User  <-- text  -->  |  cli.py     -> LibraryCLI               |
     (terminal)         |   - prints menus, reads keystrokes      |
                        |   - formats the book table              |
                        |   - catches LibraryError, prints "!!"   |
   User  <-- HTTP -->   |  web_app.py -> Flask routes             |
     (browser)          |   - reads request.form                  |
                        |   - renders Jinja templates             |
                        |   - catches LibraryError, flashes it    |
                        |                                         |
                        |  NO business rules. NO SQL. NO sqlite3. |
                        +-----------------------------------------+
                                  |                  ^
             calls service methods|                  | Book objects
             (raw strings)        |                  | or LibraryError
                                  v                  |
                        +-----------------------------------------+
                        |           BUSINESS TIER                 |
                        |              /business                  |
                        |                                         |
                        |  book_service.py -> BookService         |
                        |    orchestrates every use case          |
                        |  validators.py                          |
                        |    title/author non-empty               |
                        |    ISBN exactly 10 or 13 digits         |
                        |    year not in the future               |
                        |    quantity not negative                |
                        |    no checkout when quantity == 0       |
                        |  models.py -> Book                      |
                        |  errors.py -> LibraryError family       |
                        |  repository.py -> BookRepository (ABC)  <--- the abstraction
                        |                                         |
                        |  NO import of sqlite3 or any driver.    |
                        +-----------------------------------------+
                                  |                  ^
            calls the ABC methods |                  | Book objects
            (validated Book)      |                  | or None
                                  v                  |
                        +-----------------------------------------+
                        |             DATA TIER                   |
                        |                /data                    |
                        |                                         |
                        |  sqlite_repository.py                   |
                        |    SQLiteBookRepository  (implements ABC)|
                        |  in_memory_repository.py                |
                        |    InMemoryBookRepository(implements ABC)|
                        |                                         |
                        |  Reads/writes rows only.                |
                        |  NO validation. NO formatting.          |
                        +-----------------------------------------+
                                  |                  |
                                  v                  v
                          +--------------+   +----------------+
                          |  library.db  |   | Python list in |
                          |   (SQLite)   |   |     RAM        |
                          +--------------+   +----------------+
```

## Dependency direction

```
presentation  ---depends on--->  business  ---depends on--->  BookRepository (interface,
                                                               defined in /business)
                                                                      ^
                                                                      | implements
                                                                      |
                                                       data/SQLiteBookRepository
                                                       data/InMemoryBookRepository
```

The arrow from `data` points **up** into `business`, not down. The business tier
owns the interface; the data tier conforms to it. That inversion is what makes the
swap test possible: business code has no compile-time or import-time knowledge of
SQLite at all.

`main.py` is the composition root — the single file that is allowed to import a
concrete repository and hand it to `BookService`.

## Flow of one request: "check out book 3"

```
 1. User types "6" then "3"
        |
 2. LibraryCLI._check_out_book()           [presentation]
        |  service.check_out_book("3")
        v
 3. BookService.check_out_book()           [business]
        |  - coerces "3" to int, else ValidationError
        |  - repo.get_by_id(3)  --------------------> 4. Repository reads the row [data]
        |  <--------------------------------------------  returns Book or None
        |  - None?           -> raise BookNotFoundError
        |  - quantity == 0?  -> raise OutOfStockError    <-- the business rule
        |  - quantity -= 1
        |  - repo.update(book) ---------------------> 5. Repository writes the row [data]
        v
 6. LibraryCLI prints "Checked out 'X'. 2 copies left."
    or catches LibraryError and prints "!! <message>"
```
