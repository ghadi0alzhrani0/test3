#!/usr/bin/python3
"""Define the Place business entity."""

from app.models.amenity import Amenity
from app.models.base_model import BaseModel
from app.models.user import User


class Place(BaseModel):
    """Represent a rentable place."""

    def __init__(
        self,
        title,
        description,
        price,
        latitude,
        longitude,
        owner
    ):
        """Initialize a place with validated attributes."""
        super().__init__()
        self.title = title
        self.description = description
        self.price = price
        self.latitude = latitude
        self.longitude = longitude
        self.owner = owner
        self.reviews = []
        self.amenities = []

    @property
    def title(self):
        """Return the place title."""
        return self._title

    @title.setter
    def title(self, value):
        """Validate and set the place title."""
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Title is required")
        if len(value.strip()) > 100:
            raise ValueError("Title must be 100 characters or fewer")
        self._title = value.strip()

    @property
    def description(self):
        """Return the place description."""
        return self._description

    @description.setter
    def description(self, value):
        """Validate and set the place description."""
        if value is None:
            value = ""
        if not isinstance(value, str):
            raise ValueError("Description must be a string")
        self._description = value

    @property
    def price(self):
        """Return the nightly price."""
        return self._price

    @price.setter
    def price(self, value):
        """Validate and set the nightly price."""
        try:
            price = float(value)
        except (TypeError, ValueError) as exc:
            raise ValueError("Price must be a number") from exc

        if price < 0:
            raise ValueError("Price must be non-negative")
        self._price = price

    @property
    def latitude(self):
        """Return the latitude."""
        return self._latitude

    @latitude.setter
    def latitude(self, value):
        """Validate and set the latitude."""
        try:
            latitude = float(value)
        except (TypeError, ValueError) as exc:
            raise ValueError("Latitude must be a number") from exc

        if latitude < -90 or latitude > 90:
            raise ValueError("Latitude must be between -90 and 90")
        self._latitude = latitude

    @property
    def longitude(self):
        """Return the longitude."""
        return self._longitude

    @longitude.setter
    def longitude(self, value):
        """Validate and set the longitude."""
        try:
            longitude = float(value)
        except (TypeError, ValueError) as exc:
            raise ValueError("Longitude must be a number") from exc

        if longitude < -180 or longitude > 180:
            raise ValueError("Longitude must be between -180 and 180")
        self._longitude = longitude

    @property
    def owner(self):
        """Return the owner."""
        return self._owner

    @owner.setter
    def owner(self, value):
        """Validate and set the owner."""
        if not isinstance(value, User):
            raise ValueError("Owner must be a valid user")
        self._owner = value

    def add_review(self, review):
        """Attach a review to the place."""
        from app.models.review import Review

        if not isinstance(review, Review):
            raise ValueError("Review must be valid")
        if review not in self.reviews:
            self.reviews.append(review)
            self.save()

    def remove_review(self, review):
        """Detach a review from the place."""
        if review in self.reviews:
            self.reviews.remove(review)
            self.save()

    def add_amenity(self, amenity):
        """Attach an amenity to the place."""
        if not isinstance(amenity, Amenity):
            raise ValueError("Amenity must be valid")
        if amenity not in self.amenities:
            self.amenities.append(amenity)
            self.save()

    def set_amenities(self, amenities):
        """Replace the place amenities."""
        if amenities is None:
            amenities = []
        if not isinstance(amenities, list):
            raise ValueError("Amenities must be a list")
        if any(not isinstance(amenity, Amenity) for amenity in amenities):
            raise ValueError("Amenities must be valid")

        self.amenities = []
        for amenity in amenities:
            self.add_amenity(amenity)
        self.save()
