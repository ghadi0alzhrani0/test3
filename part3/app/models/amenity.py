#!/usr/bin/python3
"""Define the Amenity business entity."""

from sqlalchemy.orm import validates

from app import db
from app.models.base_model import BaseModel


class Amenity(BaseModel):
    """Represent an amenity that can be attached to places."""

    __tablename__ = "amenities"

    name = db.Column(db.String(50), nullable=False, unique=True)

    def __init__(self, name):
        """Initialize an amenity with a validated name."""
        super().__init__()
        self.name = name

    @validates("name")
    def validate_name(self, key, value):
        """Validate and set the amenity name."""
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Amenity name is required")
        if len(value.strip()) > 50:
            raise ValueError("Amenity name must be 50 characters or fewer")
        return value.strip()
