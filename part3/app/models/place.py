#!/usr/bin/python3
"""Define the Place business entity."""

from sqlalchemy.orm import validates

from app import db
from app.models.base_model import BaseModel


place_amenity = db.Table(
    "place_amenity",
    db.Column(
        "place_id",
        db.String(36),
        db.ForeignKey("places.id"),
        primary_key=True
    ),
    db.Column(
        "amenity_id",
        db.String(36),
        db.ForeignKey("amenities.id"),
        primary_key=True
    )
)


class Place(BaseModel):
    """Represent a rentable place."""

    __tablename__ = "places"

    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, default="", nullable=False)
    price = db.Column(db.Float, nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    owner_id = db.Column(
        db.String(36),
        db.ForeignKey("users.id"),
        nullable=False
    )

    owner = db.relationship("User", back_populates="places")
    reviews = db.relationship(
        "Review",
        back_populates="place",
        cascade="all, delete-orphan"
    )
    amenities = db.relationship(
        "Amenity",
        secondary=place_amenity,
        backref=db.backref("places", lazy=True)
    )

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

    @validates("title")
    def validate_title(self, key, value):
        """Validate and set the place title."""
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Title is required")
        if len(value.strip()) > 100:
            raise ValueError("Title must be 100 characters or fewer")
        return value.strip()

    @validates("description")
    def validate_description(self, key, value):
        """Validate and set the place description."""
        if value is None:
            value = ""
        if not isinstance(value, str):
            raise ValueError("Description must be a string")
        return value

    @validates("price")
    def validate_price(self, key, value):
        """Validate and set the nightly price."""
        try:
            price = float(value)
        except (TypeError, ValueError) as exc:
            raise ValueError("Price must be a number") from exc

        if price < 0:
            raise ValueError("Price must be non-negative")
        return price

    @validates("latitude")
    def validate_latitude(self, key, value):
        """Validate and set the latitude."""
        try:
            latitude = float(value)
        except (TypeError, ValueError) as exc:
            raise ValueError("Latitude must be a number") from exc

        if latitude < -90 or latitude > 90:
            raise ValueError("Latitude must be between -90 and 90")
        return latitude

    @validates("longitude")
    def validate_longitude(self, key, value):
        """Validate and set the longitude."""
        try:
            longitude = float(value)
        except (TypeError, ValueError) as exc:
            raise ValueError("Longitude must be a number") from exc

        if longitude < -180 or longitude > 180:
            raise ValueError("Longitude must be between -180 and 180")
        return longitude

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
        from app.models.amenity import Amenity

        if not isinstance(amenity, Amenity):
            raise ValueError("Amenity must be valid")
        if amenity not in self.amenities:
            self.amenities.append(amenity)
            self.save()

    def set_amenities(self, amenities):
        """Replace the place amenities."""
        from app.models.amenity import Amenity

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
