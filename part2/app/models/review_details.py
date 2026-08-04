#!/usr/bin/python3
"""Define detailed review entities from the Part 1 design."""

from app.models.base_model import BaseModel


def _rating(value, field):
    """Return a validated rating from 1 to 5."""
    if not isinstance(value, int) or isinstance(value, bool):
        raise ValueError(f"{field} must be an integer")
    if value < 1 or value > 5:
        raise ValueError(f"{field} must be between 1 and 5")
    return value


class ReviewRatingDetails(BaseModel):
    """Store category ratings for one place review."""

    def __init__(
        self,
        review,
        cleanliness,
        accuracy,
        communication,
        location,
        check_in,
        value
    ):
        """Initialize detailed review ratings."""
        from app.models.review import Review

        if not isinstance(review, Review):
            raise ValueError("Review must be valid")
        if review.rating_details is not None:
            raise ValueError("Review rating details already exist")
        super().__init__()
        self.review = review
        self.cleanliness = _rating(cleanliness, "Cleanliness")
        self.accuracy = _rating(accuracy, "Accuracy")
        self.communication = _rating(communication, "Communication")
        self.location = _rating(location, "Location")
        self.check_in = _rating(check_in, "Check-in")
        self.value = _rating(value, "Value")
        review.rating_details = self

    def calculate_average_rating(self):
        """Return the average of all rating categories."""
        values = (
            self.cleanliness,
            self.accuracy,
            self.communication,
            self.location,
            self.check_in,
            self.value
        )
        return sum(values) / len(values)


class ReviewResponse(BaseModel):
    """Represent an owner's response to a place review."""

    def __init__(self, review, owner, response_text):
        """Initialize a review response."""
        from app.models.owner import Owner
        from app.models.review import Review

        if not isinstance(review, Review):
            raise ValueError("Review must be valid")
        if not isinstance(owner, Owner):
            raise ValueError("Owner must be valid")
        if review.response is not None:
            raise ValueError("Review response already exists")
        if not isinstance(response_text, str) or not response_text.strip():
            raise ValueError("Response text is required")
        super().__init__()
        self.review = review
        self.owner = owner
        self.response_text = response_text.strip()
        review.response = self
        owner.respond_to_review(self)


class GuestReview(BaseModel):
    """Represent an owner's review of a guest after a booking."""

    def __init__(
        self,
        booking,
        owner,
        guest,
        cleanliness_rating,
        communication_rating,
        respect_rules_rating,
        review_text
    ):
        """Initialize a guest review."""
        from app.models.booking import Booking
        from app.models.owner import Owner
        from app.models.user import User

        if not isinstance(booking, Booking):
            raise ValueError("Booking must be valid")
        if not isinstance(owner, Owner):
            raise ValueError("Owner must be valid")
        if not isinstance(guest, User):
            raise ValueError("Guest must be valid")
        if booking.user is not guest:
            raise ValueError("Guest must match the booking user")
        if not isinstance(review_text, str) or not review_text.strip():
            raise ValueError("Review text is required")
        super().__init__()
        self.booking = booking
        self.owner = owner
        self.guest = guest
        self.cleanliness_rating = _rating(
            cleanliness_rating,
            "Cleanliness"
        )
        self.communication_rating = _rating(
            communication_rating,
            "Communication"
        )
        self.respect_rules_rating = _rating(
            respect_rules_rating,
            "Respect rules"
        )
        self.review_text = review_text.strip()
        booking.guest_review = self
        owner.review_guest(self)
        guest.guest_reviews.append(self)
