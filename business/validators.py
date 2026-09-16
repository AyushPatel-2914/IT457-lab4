"""The assignment's business rules, expressed as pure functions."""

from datetime import date

from business.errors import ValidationError

EARLIEST_YEAR = 1000


def validate_title(title) -> str:
    if not isinstance(title, str) or not title.strip():
        raise ValidationError("Title cannot be empty.")
    return title.strip()


def validate_author(author) -> str:
    if not isinstance(author, str) or not author.strip():
        raise ValidationError("Author cannot be empty.")
    return author.strip()


def validate_isbn(isbn) -> str:
    cleaned = str(isbn).replace("-", "").replace(" ", "").strip()
    if not cleaned.isdigit() or len(cleaned) not in (10, 13):
        raise ValidationError("ISBN must be exactly 10 or 13 digits.")
    return cleaned


def validate_year(year) -> int:
    try:
        value = int(year)
    except (TypeError, ValueError):
        raise ValidationError("Publication year must be a whole number.")
    current_year = date.today().year
    if value > current_year:
        raise ValidationError(
            f"Publication year cannot be in the future (max {current_year})."
        )
    if value < EARLIEST_YEAR:
        raise ValidationError(f"Publication year must be {EARLIEST_YEAR} or later.")
    return value


def validate_quantity(quantity) -> int:
    try:
        value = int(quantity)
    except (TypeError, ValueError):
        raise ValidationError("Quantity must be a whole number.")
    if value < 0:
        raise ValidationError("Quantity cannot be negative.")
    return value
