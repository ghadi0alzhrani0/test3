#!/usr/bin/python3
"""Define booking entities from the Part 1 design."""

from app.models.base_model import BaseModel
from app.models.place_details import _as_date


class Booking(BaseModel):
    """Represent a user's reservation for a place."""

    VALID_STATUSES = {
        "pending",
        "confirmed",
        "cancelled",
        "checked_in",
        "completed"
    }

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
        from app.models.place import Place
        from app.models.user import User

        if not isinstance(place, Place):
            raise ValueError("Place must be valid")
        if not isinstance(user, User):
            raise ValueError("User must be valid")
        start_date = _as_date(start_date, "Start date")
        end_date = _as_date(end_date, "End date")
        if end_date <= start_date:
            raise ValueError("End date must be after start date")
        if status not in self.VALID_STATUSES:
            raise ValueError("Invalid booking status")
        super().__init__()
        self.place = place
        self.user = user
        self.start_date = start_date
        self.end_date = end_date
        self.total_price = (
            place.calculate_total_price(start_date, end_date)
            if total_price is None else float(total_price)
        )
        if self.total_price < 0:
            raise ValueError("Total price must be non-negative")
        self.status = status
        self.guest_details = None
        self.history = []
        self.guest_review = None
        place.bookings.append(self)
        user.bookings.append(self)

    def _change_status(self, new_status):
        """Change status and append a history item."""
        old_status = self.status
        self.status = new_status
        self.history.append(BookingHistory(self, old_status, new_status))
        self.save()

    def confirm(self):
        """Confirm a pending booking."""
        self._change_status("confirmed")

    def cancel(self):
        """Cancel the booking."""
        self._change_status("cancelled")

    def check_in(self):
        """Mark a confirmed booking as checked in."""
        if self.status != "confirmed":
            raise ValueError("Only confirmed bookings can check in")
        self._change_status("checked_in")


class BookingGuest(BaseModel):
    """Store guest counts for one booking."""

    def __init__(
        self,
        booking,
        adults_count,
        children_count=0,
        infants_count=0
    ):
        """Initialize booking guest counts."""
        if not isinstance(booking, Booking):
            raise ValueError("Booking must be valid")
        counts = (adults_count, children_count, infants_count)
        if any(not isinstance(count, int) or count < 0 for count in counts):
            raise ValueError("Guest counts must be non-negative integers")
        if adults_count < 1:
            raise ValueError("At least one adult is required")
        if booking.guest_details is not None:
            raise ValueError("Booking guest details already exist")
        super().__init__()
        self.booking = booking
        self.adults_count = adults_count
        self.children_count = children_count
        self.infants_count = infants_count
        booking.guest_details = self

    def get_total_guests_count(self):
        """Return the total number of guests."""
        return self.adults_count + self.children_count + self.infants_count


class BookingHistory(BaseModel):
    """Record a booking status change."""

    def __init__(self, booking, old_status, new_status):
        """Initialize a booking history entry."""
        if not isinstance(booking, Booking):
            raise ValueError("Booking must be valid")
        if new_status not in Booking.VALID_STATUSES:
            raise ValueError("Invalid booking status")
        super().__init__()
        self.booking = booking
        self.old_status = old_status
        self.new_status = new_status
        self.changed_at = self.created_at

    def log_status_change(self):
        """Return a readable status change."""
        return f"{self.old_status} -> {self.new_status}"
