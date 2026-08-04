#!/usr/bin/python3
"""Define the Amenity business entity."""

from app.models.base_model import BaseModel


class AmenityCategory(BaseModel):
    """Represent a category that groups amenities."""

    def __init__(self, name):
        """Initialize an amenity category."""
        super().__init__()
        self.name = self._validate_name(name, "Amenity category name", 100)
        self.amenities = []

    @staticmethod
    def _validate_name(value, field, maximum):
        """Return validated name text."""
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{field} is required")
        value = value.strip()
        if len(value) > maximum:
            raise ValueError(f"{field} must be {maximum} characters or fewer")
        return value

    def add_amenity(self, amenity):
        """Attach an amenity to this category."""
        if amenity not in self.amenities:
            self.amenities.append(amenity)
            self.save()


class Amenity(BaseModel):
    """Represent an amenity that can be attached to places."""

    def __init__(self, name, description="", category=None):
        """Initialize an amenity with a validated name."""
        if category is not None and not isinstance(category, AmenityCategory):
            raise ValueError("Amenity category must be valid")
        super().__init__()
        self.name = name
        if not isinstance(description, str):
            raise ValueError("Amenity description must be a string")
        self.description = description
        self.category = category
        if category is not None:
            category.add_amenity(self)

    @property
    def name(self):
        """Return the amenity name."""
        return self._name

    @name.setter
    def name(self, value):
        """Validate and set the amenity name."""
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Amenity name is required")
        if len(value.strip()) > 50:
            raise ValueError("Amenity name must be 50 characters or fewer")
        self._name = value.strip()
