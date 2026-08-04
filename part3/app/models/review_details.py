#!/usr/bin/python3
"""Map detailed review entities with SQLAlchemy."""

from sqlalchemy.orm import validates

from app import db
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

    __tablename__ = "review_rating_details"
    __table_args__ = tuple(
        db.CheckConstraint(
            f"{field} BETWEEN 1 AND 5",
            name=f"ck_review_detail_{field}"
        )
        for field in (
            "cleanliness",
            "accuracy",
            "communication",
            "location",
            "check_in",
            "value"
        )
    )

    review_id = db.Column(
        db.String(36),
        db.ForeignKey("reviews.id"),
        nullable=False,
        unique=True
    )
    cleanliness = db.Column(db.Integer, nullable=False)
    accuracy = db.Column(db.Integer, nullable=False)
    communication = db.Column(db.Integer, nullable=False)
    location = db.Column(db.Integer, nullable=False)
    check_in = db.Column(db.Integer, nullable=False)
    value = db.Column(db.Integer, nullable=False)
    review = db.relationship("Review", back_populates="rating_details")

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
        super().__init__()
        self.review = review
        self.cleanliness = cleanliness
        self.accuracy = accuracy
        self.communication = communication
        self.location = location
        self.check_in = check_in
        self.value = value

    @validates(
        "cleanliness",
        "accuracy",
        "communication",
        "location",
        "check_in",
        "value"
    )
    def validate_rating(self, key, value):
        """Validate a detailed rating value."""
        return _rating(value, key.replace("_", " ").title())

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

    __tablename__ = "review_responses"

    review_id = db.Column(
        db.String(36),
        db.ForeignKey("reviews.id"),
        nullable=False,
        unique=True
    )
    owner_id = db.Column(
        db.String(36),
        db.ForeignKey("owners.id"),
        nullable=False
    )
    response_text = db.Column(db.Text, nullable=False)
    review = db.relationship("Review", back_populates="response")
    owner = db.relationship("Owner", back_populates="review_responses")

    def __init__(self, review, owner, response_text):
        """Initialize a review response."""
        super().__init__()
        self.review = review
        self.owner = owner
        self.response_text = response_text

    @validates("response_text")
    def validate_response_text(self, key, value):
        """Validate the response text."""
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Response text is required")
        return value.strip()


class GuestReview(BaseModel):
    """Represent an owner's review of a booking guest."""

    __tablename__ = "guest_reviews"
    __table_args__ = tuple(
        db.CheckConstraint(
            f"{field} BETWEEN 1 AND 5",
            name=f"ck_guest_review_{field}"
        )
        for field in (
            "cleanliness_rating",
            "communication_rating",
            "respect_rules_rating"
        )
    )

    booking_id = db.Column(
        db.String(36),
        db.ForeignKey("bookings.id"),
        nullable=False,
        unique=True
    )
    owner_id = db.Column(
        db.String(36),
        db.ForeignKey("owners.id"),
        nullable=False
    )
    guest_id = db.Column(
        db.String(36),
        db.ForeignKey("users.id"),
        nullable=False
    )
    cleanliness_rating = db.Column(db.Integer, nullable=False)
    communication_rating = db.Column(db.Integer, nullable=False)
    respect_rules_rating = db.Column(db.Integer, nullable=False)
    review_text = db.Column(db.Text, nullable=False)

    booking = db.relationship("Booking", back_populates="guest_review")
    owner = db.relationship("Owner", back_populates="guest_reviews")
    guest = db.relationship("User", back_populates="guest_reviews_received")

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
        if booking.user is not guest:
            raise ValueError("Guest must match the booking user")
        super().__init__()
        self.booking = booking
        self.owner = owner
        self.guest = guest
        self.cleanliness_rating = cleanliness_rating
        self.communication_rating = communication_rating
        self.respect_rules_rating = respect_rules_rating
        self.review_text = review_text

    @validates(
        "cleanliness_rating",
        "communication_rating",
        "respect_rules_rating"
    )
    def validate_rating(self, key, value):
        """Validate a guest rating value."""
        return _rating(value, key.replace("_", " ").title())

    @validates("review_text")
    def validate_review_text(self, key, value):
        """Validate guest review text."""
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Review text is required")
        return value.strip()
