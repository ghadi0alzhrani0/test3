#!/usr/bin/python3
"""Define booking, guest count, and booking history endpoints."""

from flask_restx import Namespace, Resource, fields

from app.api.v1.extended_helpers import (
    serialize_booking,
    serialize_booking_guest,
    serialize_booking_history
)
from app.services import facade


bookings_api = Namespace("bookings", description="Booking operations")
guests_api = Namespace(
    "booking-guests",
    description="Booking guest operations"
)
history_api = Namespace(
    "booking-history",
    description="Booking history lookup"
)

booking_model = bookings_api.model("Booking", {
    "place_id": fields.String(required=True),
    "user_id": fields.String(required=True),
    "start_date": fields.String(required=True, example="2026-08-10"),
    "end_date": fields.String(required=True, example="2026-08-15")
})
booking_status_model = bookings_api.model("BookingStatus", {
    "status": fields.String(
        required=True,
        enum=["confirmed", "cancelled", "checked_in"]
    )
})
guest_model = guests_api.model("BookingGuest", {
    "booking_id": fields.String(required=True),
    "adults_count": fields.Integer(required=True),
    "children_count": fields.Integer(),
    "infants_count": fields.Integer()
})
guest_update_model = guests_api.model("BookingGuestUpdate", {
    "adults_count": fields.Integer(),
    "children_count": fields.Integer(),
    "infants_count": fields.Integer()
})


@bookings_api.route("/")
class BookingList(Resource):
    """Handle the booking collection."""

    @bookings_api.expect(booking_model, validate=True)
    def post(self):
        """Create a booking."""
        try:
            booking = facade.create_booking(bookings_api.payload or {})
        except (KeyError, ValueError) as exc:
            return {"error": str(exc)}, 400
        return serialize_booking(booking), 201

    def get(self):
        """Retrieve all bookings."""
        bookings = facade.get_all_extended_resources("bookings")
        return [serialize_booking(booking) for booking in bookings], 200


@bookings_api.route("/<booking_id>")
class BookingResource(Resource):
    """Handle one booking."""

    def get(self, booking_id):
        """Retrieve a booking."""
        booking = facade.get_extended_resource("bookings", booking_id)
        if booking is None:
            return {"error": "Booking not found"}, 404
        return serialize_booking(booking), 200

    @bookings_api.expect(booking_status_model, validate=True)
    def put(self, booking_id):
        """Apply a booking status transition."""
        try:
            booking = facade.update_booking_status(
                booking_id, (bookings_api.payload or {}).get("status")
            )
        except ValueError as exc:
            return {"error": str(exc)}, 400
        return serialize_booking(booking), 200


@guests_api.route("/")
class BookingGuestList(Resource):
    """Handle the booking guest collection."""

    @guests_api.expect(guest_model, validate=True)
    def post(self):
        """Add guest counts to a booking."""
        try:
            details = facade.create_booking_guest(guests_api.payload or {})
        except ValueError as exc:
            return {"error": str(exc)}, 400
        return serialize_booking_guest(details), 201

    def get(self):
        """Retrieve all booking guest records."""
        details = facade.get_all_extended_resources("booking_guests")
        return [serialize_booking_guest(item) for item in details], 200


@guests_api.route("/<details_id>")
class BookingGuestResource(Resource):
    """Handle one booking guest record."""

    def get(self, details_id):
        """Retrieve booking guest counts."""
        details = facade.get_extended_resource("booking_guests", details_id)
        if details is None:
            return {"error": "Booking guest details not found"}, 404
        return serialize_booking_guest(details), 200

    @guests_api.expect(guest_update_model, validate=True)
    def put(self, details_id):
        """Update booking guest counts."""
        try:
            details = facade.update_extended_resource(
                "booking_guests", details_id, guests_api.payload or {}
            )
        except ValueError as exc:
            return {"error": str(exc)}, 400
        if details is None:
            return {"error": "Booking guest details not found"}, 404
        return serialize_booking_guest(details), 200


@history_api.route("/")
class BookingHistoryList(Resource):
    """Handle the read-only booking history collection."""

    def get(self):
        """Retrieve all booking status changes."""
        history = facade.get_all_extended_resources("booking_history")
        return [serialize_booking_history(item) for item in history], 200


@history_api.route("/<history_id>")
class BookingHistoryResource(Resource):
    """Handle one read-only booking history record."""

    def get(self, history_id):
        """Retrieve one booking status change."""
        history = facade.get_extended_resource("booking_history", history_id)
        if history is None:
            return {"error": "Booking history not found"}, 404
        return serialize_booking_history(history), 200
