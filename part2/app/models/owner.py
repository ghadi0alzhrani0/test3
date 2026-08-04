#!/usr/bin/python3
"""Define the business owner entity from the Part 1 design."""

from app.models.base_model import BaseModel
from app.models.user import EMAIL_PATTERN


class Owner(BaseModel):
    """Represent a business owner who manages places."""

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
        self.business_name = self._required(business_name, "Business name")
        self.contact_person = self._required(
            contact_person,
            "Contact person"
        )
        self.email = self._validate_email(email)
        self.password = self._required(password, "Password", 128)
        self.phone_number = self._required(phone_number, "Phone number", 30)
        self.commercial_register = self._required(
            commercial_register,
            "Commercial register",
            50
        )
        self.places = []
        self.review_responses = []
        self.guest_reviews = []
        self.notifications = []

    @staticmethod
    def _required(value, field, maximum=255):
        """Validate required owner text."""
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{field} is required")
        value = value.strip()
        if len(value) > maximum:
            raise ValueError(f"{field} must be {maximum} characters or fewer")
        return value

    @staticmethod
    def _validate_email(value):
        """Validate an owner email address."""
        value = Owner._required(value, "Email", 120).lower()
        if not EMAIL_PATTERN.match(value):
            raise ValueError("Invalid email format")
        return value

    def add_place(self, place):
        """Attach a managed place."""
        if place not in self.places:
            self.places.append(place)
            self.save()

    def add_seasonal_pricing(self, place, pricing):
        """Attach seasonal pricing to one of the owner's places."""
        if place not in self.places:
            raise ValueError("Owner does not manage this place")
        place.add_seasonal_pricing(pricing)

    def respond_to_review(self, response):
        """Store a response written by the owner."""
        if response not in self.review_responses:
            self.review_responses.append(response)
            self.save()

    def review_guest(self, review):
        """Store a review written about a guest."""
        if review not in self.guest_reviews:
            self.guest_reviews.append(review)
            self.save()
