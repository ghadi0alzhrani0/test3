#!/usr/bin/python3
"""Define the Amenity business entity."""

from sqlalchemy.orm import validates

from app import db
from app.models.base_model import BaseModel


class AmenityCategory(BaseModel):
    """Represent a category that groups amenities."""

    __tablename__ = "amenity_categories"

    name = db.Column(db.String(100), nullable=False, unique=True)
    amenities = db.relationship(
        "Amenity",
        back_populates="category"
    )

    def __init__(self, name):
        """Initialize an amenity category."""
        super().__init__()
        self.name = name

    @validates("name")
    def validate_name(self, key, value):
        """Validate the category name."""
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Amenity category name is required")
        if len(value.strip()) > 100:
            raise ValueError(
                "Amenity category name must be 100 characters or fewer"
            )
        return value.strip()


class Amenity(BaseModel):
    """Represent an amenity that can be attached to places."""

    __tablename__ = "amenities"

    name = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.Text, default="", nullable=False)
    category_id = db.Column(
        db.String(36),
        db.ForeignKey("amenity_categories.id"),
        nullable=True
    )
    category = db.relationship("AmenityCategory", back_populates="amenities")

    def __init__(self, name, description="", category=None):
        """Initialize an amenity with a validated name."""
        super().__init__()
        self.name = name
        self.description = description
        self.category = category

    @validates("name")
    def validate_name(self, key, value):
        """Validate and set the amenity name."""
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Amenity name is required")
        if len(value.strip()) > 50:
            raise ValueError("Amenity name must be 50 characters or fewer")
        return value.strip()

    @validates("description")
    def validate_description(self, key, value):
        """Validate the amenity description."""
        if not isinstance(value, str):
            raise ValueError("Amenity description must be a string")
        return value
