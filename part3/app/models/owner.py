#!/usr/bin/python3
"""Map the business owner entity from the Part 1 design."""

from sqlalchemy.orm import validates

from app import bcrypt, db
from app.models.base_model import BaseModel
from app.models.user import EMAIL_PATTERN


class Owner(BaseModel):
    """Represent a business owner who manages places."""

    __tablename__ = "owners"

    business_name = db.Column(db.String(255), nullable=False)
    contact_person = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(128), nullable=False)
    phone_number = db.Column(db.String(30), nullable=False)
    commercial_register = db.Column(
        db.String(50),
        nullable=False,
        unique=True
    )

    places = db.relationship("Place", back_populates="business_owner")
    review_responses = db.relationship(
        "ReviewResponse",
        back_populates="owner",
        cascade="all, delete-orphan"
    )
    guest_reviews = db.relationship(
        "GuestReview",
        back_populates="owner",
        cascade="all, delete-orphan"
    )
    notifications = db.relationship(
        "SystemNotification",
        back_populates="owner",
        cascade="all, delete-orphan"
    )

    def __init__(
        self,
        business_name,
        contact_person,
        email,
        password,
        phone_number,
        commercial_register
    ):
        """Initialize a business owner."""
        super().__init__()
        self.business_name = business_name
        self.contact_person = contact_person
        self.email = email
        self.hash_password(password)
        self.phone_number = phone_number
        self.commercial_register = commercial_register

    def hash_password(self, password):
        """Hash and store the owner password."""
        if not isinstance(password, str) or not password:
            raise ValueError("Password is required")
        self.password = bcrypt.generate_password_hash(password).decode("utf-8")

    def verify_password(self, password):
        """Check a plaintext owner password."""
        return (
            isinstance(password, str)
            and bcrypt.check_password_hash(self.password, password)
        )

    @staticmethod
    def _required(value, field, maximum):
        """Return validated owner text."""
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{field} is required")
        value = value.strip()
        if len(value) > maximum:
            raise ValueError(f"{field} must be {maximum} characters or fewer")
        return value

    @validates(
        "business_name",
        "contact_person",
        "phone_number",
        "commercial_register"
    )
    def validate_text(self, key, value):
        """Validate required owner fields."""
        labels = {
            "business_name": ("Business name", 255),
            "contact_person": ("Contact person", 100),
            "phone_number": ("Phone number", 30),
            "commercial_register": ("Commercial register", 50)
        }
        label, maximum = labels[key]
        return self._required(value, label, maximum)

    @validates("email")
    def validate_email(self, key, value):
        """Validate and normalize the owner email."""
        value = self._required(value, "Email", 120).lower()
        if not EMAIL_PATTERN.match(value):
            raise ValueError("Invalid email format")
        return value
