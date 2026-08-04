#!/usr/bin/python3
"""Map supporting place entities with SQLAlchemy."""

from datetime import date

from sqlalchemy.orm import validates

from app import db
from app.models.base_model import BaseModel


def _required(value, field, maximum=100):
    """Return validated required text."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} is required")
    value = value.strip()
    if len(value) > maximum:
        raise ValueError(f"{field} must be {maximum} characters or fewer")
    return value


def _as_date(value, field):
    """Return a date from a date object or ISO date string."""
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        try:
            return date.fromisoformat(value)
        except ValueError as exc:
            raise ValueError(f"{field} must use YYYY-MM-DD") from exc
    raise ValueError(f"{field} must be a date")


class PlaceType(BaseModel):
    """Represent a category such as apartment or villa."""

    __tablename__ = "place_types"

    name = db.Column(db.String(100), nullable=False, unique=True)
    places = db.relationship("Place", back_populates="place_type")

    def __init__(self, name):
        """Initialize a place type."""
        super().__init__()
        self.name = name

    @validates("name")
    def validate_name(self, key, value):
        """Validate the place type name."""
        return _required(value, "Place type name")


class CancellationPolicy(BaseModel):
    """Represent cancellation rules for a place."""

    __tablename__ = "cancellation_policies"

    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=False)
    places = db.relationship("Place", back_populates="cancellation_policy")

    def __init__(self, name, description):
        """Initialize a cancellation policy."""
        super().__init__()
        self.name = name
        self.description = description

    @validates("name")
    def validate_name(self, key, value):
        """Validate the policy name."""
        return _required(value, "Policy name")

    @validates("description")
    def validate_description(self, key, value):
        """Validate the policy description."""
        return _required(value, "Policy description", 1000)

    def calculate_refund(self, total_price, days_before):
        """Calculate a simple full, partial, or zero refund."""
        total_price = float(total_price)
        days_before = int(days_before)
        if total_price < 0 or days_before < 0:
            raise ValueError("Price and days must be non-negative")
        if days_before >= 7:
            return total_price
        if days_before >= 2:
            return total_price * 0.5
        return 0.0


class RoomDetail(BaseModel):
    """Describe a room inside a place."""

    __tablename__ = "room_details"

    place_id = db.Column(
        db.String(36),
        db.ForeignKey("places.id"),
        nullable=False
    )
    room_name = db.Column(db.String(100), nullable=False)
    bed_type = db.Column(db.String(100), nullable=False)
    beds_count = db.Column(db.Integer, nullable=False)
    place = db.relationship("Place", back_populates="room_details")

    def __init__(self, place, room_name, bed_type, beds_count):
        """Initialize room details."""
        super().__init__()
        self.place = place
        self.room_name = room_name
        self.bed_type = bed_type
        self.beds_count = beds_count

    @validates("room_name", "bed_type")
    def validate_text(self, key, value):
        """Validate room text fields."""
        label = "Room name" if key == "room_name" else "Bed type"
        return _required(value, label)

    @validates("beds_count")
    def validate_beds_count(self, key, value):
        """Validate the number of beds."""
        if not isinstance(value, int) or value < 1:
            raise ValueError("Beds count must be a positive integer")
        return value


class PlaceAvailability(BaseModel):
    """Represent a date range in a place calendar."""

    __tablename__ = "place_availability"
    __table_args__ = (
        db.CheckConstraint(
            "end_date > start_date",
            name="ck_availability_dates"
        ),
    )

    place_id = db.Column(
        db.String(36),
        db.ForeignKey("places.id"),
        nullable=False
    )
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    is_booked = db.Column(db.Boolean, default=False, nullable=False)
    place = db.relationship("Place", back_populates="availability_periods")

    def __init__(self, place, start_date, end_date, is_booked=False):
        """Initialize an availability period."""
        super().__init__()
        self.place = place
        self.start_date = _as_date(start_date, "Start date")
        self.end_date = _as_date(end_date, "End date")
        if self.end_date <= self.start_date:
            raise ValueError("End date must be after start date")
        self.is_booked = is_booked

    @validates("is_booked")
    def validate_is_booked(self, key, value):
        """Validate the booked flag."""
        if not isinstance(value, bool):
            raise ValueError("is_booked must be a boolean")
        return value

    def toggle_availability(self):
        """Switch the booked state for this period."""
        self.is_booked = not self.is_booked
        self.save()
        return self.is_booked


class SeasonalPricing(BaseModel):
    """Represent a special price active during a date range."""

    __tablename__ = "seasonal_pricing"
    __table_args__ = (
        db.CheckConstraint("end_date > start_date", name="ck_pricing_dates"),
        db.CheckConstraint("special_price >= 0", name="ck_special_price")
    )

    place_id = db.Column(
        db.String(36),
        db.ForeignKey("places.id"),
        nullable=False
    )
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    special_price = db.Column(db.Float, nullable=False)
    place = db.relationship("Place", back_populates="seasonal_pricing")

    def __init__(self, place, start_date, end_date, special_price):
        """Initialize seasonal pricing."""
        super().__init__()
        self.place = place
        self.start_date = _as_date(start_date, "Start date")
        self.end_date = _as_date(end_date, "End date")
        if self.end_date <= self.start_date:
            raise ValueError("End date must be after start date")
        self.special_price = special_price

    @validates("special_price")
    def validate_special_price(self, key, value):
        """Validate the special nightly price."""
        value = float(value)
        if value < 0:
            raise ValueError("Special price must be non-negative")
        return value

    def is_active(self, requested_date):
        """Return whether the special price applies on a date."""
        requested_date = _as_date(requested_date, "Requested date")
        return self.start_date <= requested_date <= self.end_date
