#!/usr/bin/python3
"""Define the Review business entity."""

from sqlalchemy.orm import validates

from app import db
from app.models.base_model import BaseModel


class Review(BaseModel):
    """Represent a user's review for a place."""

    __tablename__ = "reviews"
    __table_args__ = (
        db.UniqueConstraint(
            "user_id",
            "place_id",
            name="uq_review_user_place"
        ),
    )

    text = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    place_id = db.Column(
        db.String(36),
        db.ForeignKey("places.id"),
        nullable=False
    )
    user_id = db.Column(
        db.String(36),
        db.ForeignKey("users.id"),
        nullable=False
    )

    place = db.relationship("Place", back_populates="reviews")
    user = db.relationship("User", back_populates="reviews")

    def __init__(self, text, rating, place, user):
        """Initialize a review with validated attributes."""
        super().__init__()
        self.text = text
        self.rating = rating
        self.place = place
        self.user = user

    @validates("text")
    def validate_text(self, key, value):
        """Validate and set the review text."""
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Review text is required")
        return value.strip()

    @validates("rating")
    def validate_rating(self, key, value):
        """Validate and set the rating."""
        if not isinstance(value, int) or isinstance(value, bool):
            raise ValueError("Rating must be an integer")
        if value < 1 or value > 5:
            raise ValueError("Rating must be between 1 and 5")
        return value
