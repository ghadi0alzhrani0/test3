#!/usr/bin/python3
"""Define supporting place entities from the Part 1 design."""

from datetime import date

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

    def __init__(self, name):
        """Initialize a place type."""
        super().__init__()
        self.name = _required(name, "Place type name")
        self.places = []


class CancellationPolicy(BaseModel):
    """Represent cancellation rules for a place."""

    def __init__(self, name, description):
        """Initialize a cancellation policy."""
        super().__init__()
        self.name = _required(name, "Policy name")
        self.description = _required(description, "Policy description", 1000)
        self.places = []

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

    def __init__(self, place, room_name, bed_type, beds_count):
        """Initialize room details."""
        from app.models.place import Place

        if not isinstance(place, Place):
            raise ValueError("Place must be valid")
        if not isinstance(beds_count, int) or beds_count < 1:
            raise ValueError("Beds count must be a positive integer")
        super().__init__()
        self.place = place
        self.room_name = _required(room_name, "Room name")
        self.bed_type = _required(bed_type, "Bed type")
        self.beds_count = beds_count
        place.add_room_detail(self)


class PlaceAvailability(BaseModel):
    """Represent a date range in a place calendar."""

    def __init__(self, place, start_date, end_date, is_booked=False):
        """Initialize an availability period."""
        from app.models.place import Place

        if not isinstance(place, Place):
            raise ValueError("Place must be valid")
        start_date = _as_date(start_date, "Start date")
        end_date = _as_date(end_date, "End date")
        if end_date <= start_date:
            raise ValueError("End date must be after start date")
        if not isinstance(is_booked, bool):
            raise ValueError("is_booked must be a boolean")
        super().__init__()
        self.place = place
        self.start_date = start_date
        self.end_date = end_date
        self.is_booked = is_booked
        place.add_availability(self)

    def toggle_availability(self):
        """Switch the booked state for this period."""
        self.is_booked = not self.is_booked
        self.save()
        return self.is_booked


class SeasonalPricing(BaseModel):
    """Represent a special price active during a date range."""

    def __init__(self, place, start_date, end_date, special_price):
        """Initialize seasonal pricing."""
        from app.models.place import Place

        if not isinstance(place, Place):
            raise ValueError("Place must be valid")
        start_date = _as_date(start_date, "Start date")
        end_date = _as_date(end_date, "End date")
        if end_date <= start_date:
            raise ValueError("End date must be after start date")
        special_price = float(special_price)
        if special_price < 0:
            raise ValueError("Special price must be non-negative")
        super().__init__()
        self.place = place
        self.start_date = start_date
        self.end_date = end_date
        self.special_price = special_price
        place.add_seasonal_pricing(self)

    def is_active(self, requested_date):
        """Return whether the special price applies on a date."""
        requested_date = _as_date(requested_date, "Requested date")
        return self.start_date <= requested_date <= self.end_date
