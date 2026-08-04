#!/usr/bin/python3
"""Map booking entities with SQLAlchemy."""

from sqlalchemy.orm import validates

from app import db
from app.models.base_model import BaseModel
from app.models.place_details import _as_date


class Booking(BaseModel):
    """Represent a user's reservation for a place."""

    __tablename__ = "bookings"
    __table_args__ = (
        db.CheckConstraint("end_date > start_date", name="ck_booking_dates"),
        db.CheckConstraint("total_price >= 0", name="ck_booking_price"),
        db.CheckConstraint(
            "status IN ('pending', 'confirmed', 'cancelled', "
            "'checked_in', 'completed')",
            name="ck_booking_status"
        )
    )

    VALID_STATUSES = {
        "pending",
        "confirmed",
        "cancelled",
        "checked_in",
        "completed"
    }

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
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default="pending", nullable=False)

    place = db.relationship("Place", back_populates="bookings")
    user = db.relationship("User", back_populates="bookings")
    guest_details = db.relationship(
        "BookingGuest",
        back_populates="booking",
        cascade="all, delete-orphan",
        uselist=False
    )
    history = db.relationship(
        "BookingHistory",
        back_populates="booking",
        cascade="all, delete-orphan",
        order_by="BookingHistory.changed_at"
    )
    guest_review = db.relationship(
        "GuestReview",
        back_populates="booking",
        cascade="all, delete-orphan",
        uselist=False
    )

    def __init__(
        self,
        place,
        user,
        start_date,
        end_date,
        total_price=None,
        status="pending"
    ):
        """Initialize a booking."""
        super().__init__()
        parsed_start_date = _as_date(start_date, "Start date")
        parsed_end_date = _as_date(end_date, "End date")
        if parsed_end_date <= parsed_start_date:
            raise ValueError("End date must be after start date")

        calculated_price = (
            place.calculate_total_price(parsed_start_date, parsed_end_date)
            if total_price is None else total_price
        )

        self.place = place
        self.user = user
        self.start_date = parsed_start_date
        self.end_date = parsed_end_date
        self.total_price = calculated_price
        self.status = status

    @validates("total_price")
    def validate_total_price(self, key, value):
        """Validate the booking total."""
        value = float(value)
        if value < 0:
            raise ValueError("Total price must be non-negative")
        return value

    @validates("status")
    def validate_status(self, key, value):
        """Validate the booking status."""
        if value not in self.VALID_STATUSES:
            raise ValueError("Invalid booking status")
        return value

    def _change_status(self, new_status):
        """Change status and append a history record."""
        old_status = self.status
        self.status = new_status
        history = BookingHistory(self, old_status, new_status)
        self.save()
        return history

    def confirm(self):
        """Confirm a pending booking."""
        return self._change_status("confirmed")

    def cancel(self):
        """Cancel the booking."""
        return self._change_status("cancelled")

    def check_in(self):
        """Mark a confirmed booking as checked in."""
        if self.status != "confirmed":
            raise ValueError("Only confirmed bookings can check in")
        return self._change_status("checked_in")


class BookingGuest(BaseModel):
    """Store guest counts for one booking."""

    __tablename__ = "booking_guests"
    __table_args__ = (
        db.CheckConstraint("adults_count >= 1", name="ck_guest_adults"),
        db.CheckConstraint("children_count >= 0", name="ck_guest_children"),
        db.CheckConstraint("infants_count >= 0", name="ck_guest_infants")
    )

    booking_id = db.Column(
        db.String(36),
        db.ForeignKey("bookings.id"),
        nullable=False,
        unique=True
    )
    adults_count = db.Column(db.Integer, nullable=False)
    children_count = db.Column(db.Integer, default=0, nullable=False)
    infants_count = db.Column(db.Integer, default=0, nullable=False)
    booking = db.relationship("Booking", back_populates="guest_details")

    def __init__(
        self,
        booking,
        adults_count,
        children_count=0,
        infants_count=0
    ):
        """Initialize booking guest counts."""
        super().__init__()
        self.booking = booking
        self.adults_count = adults_count
        self.children_count = children_count
        self.infants_count = infants_count

    @validates("adults_count", "children_count", "infants_count")
    def validate_count(self, key, value):
        """Validate a guest count."""
        if not isinstance(value, int) or value < 0:
            raise ValueError("Guest counts must be non-negative integers")
        if key == "adults_count" and value < 1:
            raise ValueError("At least one adult is required")
        return value

    def get_total_guests_count(self):
        """Return the total number of guests."""
        return self.adults_count + self.children_count + self.infants_count


class BookingHistory(BaseModel):
    """Record a booking status change."""

    __tablename__ = "booking_history"

    booking_id = db.Column(
        db.String(36),
        db.ForeignKey("bookings.id"),
        nullable=False
    )
    old_status = db.Column(db.String(20), nullable=False)
    new_status = db.Column(db.String(20), nullable=False)
    changed_at = db.Column(db.DateTime, nullable=False)
    booking = db.relationship("Booking", back_populates="history")

    def __init__(self, booking, old_status, new_status):
        """Initialize a booking history entry."""
        super().__init__()
        self.booking = booking
        self.old_status = old_status
        self.new_status = new_status
        self.changed_at = self.created_at

    def log_status_change(self):
        """Return a readable status change."""
        return f"{self.old_status} -> {self.new_status}"
