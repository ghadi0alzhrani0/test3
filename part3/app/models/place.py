#!/usr/bin/python3
"""Define the Place business entity."""

from datetime import date

from sqlalchemy.orm import validates

from app import db
from app.models.base_model import BaseModel
from app.models.place_details import _as_date


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
    __table_args__ = (
        db.CheckConstraint("price >= 0", name="ck_place_price"),
        db.CheckConstraint(
            "latitude BETWEEN -90 AND 90",
            name="ck_place_latitude"
        ),
        db.CheckConstraint(
            "longitude BETWEEN -180 AND 180",
            name="ck_place_longitude"
        ),
        db.CheckConstraint("number_rooms >= 0", name="ck_place_rooms"),
        db.CheckConstraint(
            "number_bathrooms >= 0",
            name="ck_place_bathrooms"
        ),
        db.CheckConstraint("max_guest >= 1", name="ck_place_guests")
    )

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
    business_owner_id = db.Column(
        db.String(36),
        db.ForeignKey("owners.id"),
        nullable=True
    )
    city_id = db.Column(
        db.String(36),
        db.ForeignKey("cities.id"),
        nullable=True
    )
    place_type_id = db.Column(
        db.String(36),
        db.ForeignKey("place_types.id"),
        nullable=True
    )
    cancellation_policy_id = db.Column(
        db.String(36),
        db.ForeignKey("cancellation_policies.id"),
        nullable=True
    )
    number_rooms = db.Column(db.Integer, default=0, nullable=False)
    number_bathrooms = db.Column(db.Integer, default=0, nullable=False)
    max_guest = db.Column(db.Integer, default=1, nullable=False)

    owner = db.relationship("User", back_populates="places")
    business_owner = db.relationship("Owner", back_populates="places")
    city = db.relationship("City", back_populates="places")
    place_type = db.relationship("PlaceType", back_populates="places")
    cancellation_policy = db.relationship(
        "CancellationPolicy",
        back_populates="places"
    )
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
    room_details = db.relationship(
        "RoomDetail",
        back_populates="place",
        cascade="all, delete-orphan"
    )
    availability_periods = db.relationship(
        "PlaceAvailability",
        back_populates="place",
        cascade="all, delete-orphan"
    )
    seasonal_pricing = db.relationship(
        "SeasonalPricing",
        back_populates="place",
        cascade="all, delete-orphan"
    )
    bookings = db.relationship(
        "Booking",
        back_populates="place",
        cascade="all, delete-orphan"
    )

    def __init__(
        self,
        title,
        description,
        price,
        latitude,
        longitude,
        owner,
        city=None,
        place_type=None,
        cancellation_policy=None,
        number_rooms=0,
        number_bathrooms=0,
        max_guest=1,
        business_owner=None
    ):
        """Initialize a place with validated attributes."""
        super().__init__()
        self.title = title
        self.description = description
        self.price = price
        self.latitude = latitude
        self.longitude = longitude
        self.owner = owner
        self.city = city
        self.place_type = place_type
        self.cancellation_policy = cancellation_policy
        self.business_owner = business_owner
        self.number_rooms = number_rooms
        self.number_bathrooms = number_bathrooms
        self.max_guest = max_guest

    @property
    def name(self):
        """Return the Part 1 name alias for the place title."""
        return self.title

    @name.setter
    def name(self, value):
        """Update the place title through its Part 1 alias."""
        self.title = value

    @property
    def price_by_night(self):
        """Return the Part 1 alias for the nightly price."""
        return self.price

    @price_by_night.setter
    def price_by_night(self, value):
        """Update the nightly price through its Part 1 alias."""
        self.price = value

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

    @validates("number_rooms", "number_bathrooms", "max_guest")
    def validate_count(self, key, value):
        """Validate place count fields."""
        if not isinstance(value, int) or isinstance(value, bool):
            raise ValueError("Place counts must be integers")
        minimum = 1 if key == "max_guest" else 0
        if value < minimum:
            raise ValueError(f"{key} must be at least {minimum}")
        return value

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

    def check_availability(self, start_date, end_date):
        """Return whether a place is free for the requested range."""
        start_date = _as_date(start_date, "Start date")
        end_date = _as_date(end_date, "End date")
        if end_date <= start_date:
            raise ValueError("End date must be after start date")
        for period in self.availability_periods:
            overlaps = (
                start_date < period.end_date
                and end_date > period.start_date
            )
            if overlaps and period.is_booked:
                return False
        for booking in self.bookings:
            overlaps = (
                start_date < booking.end_date
                and end_date > booking.start_date
            )
            if overlaps and booking.status not in {"cancelled", "completed"}:
                return False
        return True

    def calculate_total_price(self, start_date, end_date):
        """Calculate the nightly total, including seasonal prices."""
        start_date = _as_date(start_date, "Start date")
        end_date = _as_date(end_date, "End date")
        if end_date <= start_date:
            raise ValueError("End date must be after start date")
        total = 0.0
        current = start_date
        while current < end_date:
            price = self.price
            for seasonal in self.seasonal_pricing:
                if seasonal.is_active(current):
                    price = seasonal.special_price
                    break
            total += price
            current = date.fromordinal(current.toordinal() + 1)
        return total

    def get_average_ratings(self):
        """Return the average rating from all place reviews."""
        if not self.reviews:
            return 0.0
        total = sum(review.rating for review in self.reviews)
        return total / len(self.reviews)
