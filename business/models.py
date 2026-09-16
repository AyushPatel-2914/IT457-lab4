"""The domain model shared across tiers."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Book:
    title: str
    author: str
    isbn: str
    year: int
    quantity: int
    id: Optional[int] = None
