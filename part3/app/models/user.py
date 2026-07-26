#!/usr/bin/python3
"""Define the User business entity."""

import re

from sqlalchemy.orm import validates

from app import bcrypt, db
from app.models.base_model import BaseModel


EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class User(BaseModel):
    """Represent an HBnB user."""

    __tablename__ = "users"

    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)

    places = db.relationship(
        "Place",
        back_populates="owner",
        cascade="all, delete-orphan"
    )
    reviews = db.relationship(
        "Review",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    def __init__(
        self,
        first_name,
        last_name,
        email,
        password,
        is_admin=False
    ):
        """Initialize a user with validated attributes."""
        super().__init__()
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.hash_password(password)
        self.is_admin = is_admin

    def hash_password(self, password):
        """Hash and store a plaintext password."""
        if not isinstance(password, str) or not password:
            raise ValueError("Password is required")
        self.password = bcrypt.generate_password_hash(password).decode("utf-8")

    def verify_password(self, password):
        """Return whether a plaintext password matches the stored hash."""
        if not isinstance(password, str):
            return False
        return bcrypt.check_password_hash(self.password, password)

    @validates("first_name")
    def validate_first_name(self, key, value):
        """Validate and set the user's first name."""
        if not isinstance(value, str) or not value.strip():
            raise ValueError("First name is required")
        if len(value.strip()) > 50:
            raise ValueError("First name must be 50 characters or fewer")
        return value.strip()

    @validates("last_name")
    def validate_last_name(self, key, value):
        """Validate and set the user's last name."""
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Last name is required")
        if len(value.strip()) > 50:
            raise ValueError("Last name must be 50 characters or fewer")
        return value.strip()

    @validates("email")
    def validate_email(self, key, value):
        """Validate and set the user's email."""
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Email is required")

        email = value.strip().lower()
        if not EMAIL_PATTERN.match(email):
            raise ValueError("Invalid email format")

        return email

    @validates("is_admin")
    def validate_is_admin(self, key, value):
        """Validate and set the admin flag."""
        if not isinstance(value, bool):
            raise ValueError("is_admin must be a boolean")
        return value
