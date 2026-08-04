#!/usr/bin/python3
"""Define the User business entity."""

import re

from app.models.base_model import BaseModel


EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class User(BaseModel):
    """Represent an HBnB user."""

    def __init__(self, first_name, last_name, email, is_admin=False):
        """Initialize a user with validated attributes."""
        super().__init__()
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.is_admin = is_admin
        self.places = []
        self.bookings = []
        self.reviews = []
        self.guest_reviews = []
        self.notifications = []

    def register(self):
        """Return the registered user identifier."""
        return self.id

    def login(self, email):
        """Check whether an email belongs to this user."""
        return isinstance(email, str) and self.email.lower() == email.lower()

    def book_place(self, booking):
        """Attach a booking to the user."""
        if booking not in self.bookings:
            self.bookings.append(booking)
            self.save()

    def add_review(self, review):
        """Attach a place review written by the user."""
        if review not in self.reviews:
            self.reviews.append(review)
            self.save()

    @property
    def first_name(self):
        """Return the user's first name."""
        return self._first_name

    @first_name.setter
    def first_name(self, value):
        """Validate and set the user's first name."""
        if not isinstance(value, str) or not value.strip():
            raise ValueError("First name is required")
        if len(value.strip()) > 50:
            raise ValueError("First name must be 50 characters or fewer")
        self._first_name = value.strip()

    @property
    def last_name(self):
        """Return the user's last name."""
        return self._last_name

    @last_name.setter
    def last_name(self, value):
        """Validate and set the user's last name."""
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Last name is required")
        if len(value.strip()) > 50:
            raise ValueError("Last name must be 50 characters or fewer")
        self._last_name = value.strip()

    @property
    def email(self):
        """Return the user's email."""
        return self._email

    @email.setter
    def email(self, value):
        """Validate and set the user's email."""
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Email is required")

        email = value.strip()
        if not EMAIL_PATTERN.match(email):
            raise ValueError("Invalid email format")

        self._email = email

    @property
    def is_admin(self):
        """Return whether the user is an administrator."""
        return self._is_admin

    @is_admin.setter
    def is_admin(self, value):
        """Validate and set the admin flag."""
        if not isinstance(value, bool):
            raise ValueError("is_admin must be a boolean")
        self._is_admin = value
