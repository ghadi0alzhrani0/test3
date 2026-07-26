#!/usr/bin/python3
"""Define the Review business entity."""

from app.models.base_model import BaseModel
from app.models.place import Place
from app.models.user import User


class Review(BaseModel):
    """Represent a user's review for a place."""

    def __init__(self, text, rating, place, user):
        """Initialize a review with validated attributes."""
        super().__init__()
        self.text = text
        self.rating = rating
        self.place = place
        self.user = user

    @property
    def text(self):
        """Return the review text."""
        return self._text

    @text.setter
    def text(self, value):
        """Validate and set the review text."""
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Review text is required")
        self._text = value.strip()

    @property
    def rating(self):
        """Return the rating."""
        return self._rating

    @rating.setter
    def rating(self, value):
        """Validate and set the rating."""
        if not isinstance(value, int) or isinstance(value, bool):
            raise ValueError("Rating must be an integer")
        if value < 1 or value > 5:
            raise ValueError("Rating must be between 1 and 5")
        self._rating = value

    @property
    def place(self):
        """Return the reviewed place."""
        return self._place

    @place.setter
    def place(self, value):
        """Validate and set the reviewed place."""
        if not isinstance(value, Place):
            raise ValueError("Place must be valid")
        self._place = value

    @property
    def user(self):
        """Return the review author."""
        return self._user

    @user.setter
    def user(self, value):
        """Validate and set the review author."""
        if not isinstance(value, User):
            raise ValueError("User must be valid")
        self._user = value
