"""Error types raised by the business tier and translated by the presentation tier."""


class LibraryError(Exception):
    """Base class for every error the business tier raises."""


class ValidationError(LibraryError):
    """Input failed one of the validation rules."""


class BookNotFoundError(LibraryError):
    """No book exists with the requested id."""


class DuplicateISBNError(LibraryError):
    """Another book in the collection already uses this ISBN."""


class OutOfStockError(LibraryError):
    """A checkout was attempted while quantity was already 0."""
