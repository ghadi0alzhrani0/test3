#!/usr/bin/python3
"""Define the Amenity business entity."""

from app.models.base_model import BaseModel


class Amenity(BaseModel):
    """Represent an amenity that can be attached to places."""

    def __init__(self, name):
        """Initialize an amenity with a validated name."""
        super().__init__()
        self.name = name

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
