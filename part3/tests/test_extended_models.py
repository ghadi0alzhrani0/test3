#!/usr/bin/python3
"""Tests for the extended Part 1 database design in Part 3."""

import unittest

from app import create_app, db
from app.models.booking import Booking
from app.models.location import City
from app.models.notification import SystemNotification
from app.models.owner import Owner
from app.services import facade


class TestConfig:
    """Use a separate in-memory database for tests."""

    TESTING = True
    SECRET_KEY = "extended-model-test-key"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class TestExtendedDatabaseModels(unittest.TestCase):
    """Exercise persistence for all entities carried from Part 1."""

    def setUp(self):
        """Create a clean mapped database and connected place."""
        self.app = create_app(TestConfig)
        self.context = self.app.app_context()
        self.context.push()
        db.create_all()

        self.user = facade.create_user({
            "first_name": "Sara",
            "last_name": "Guest",
            "email": "sara.extended@example.com",
            "password": "guest-password"
        })
        self.owner = facade.create_owner({
            "business_name": "Riyadh Stays",
            "contact_person": "Nora Owner",
            "email": "owner.extended@example.com",
            "password": "owner-password",
            "phone_number": "+966500000000",
            "commercial_register": "CR-EXTENDED-1"
        })
        country = facade.create_country({
            "name": "Saudi Arabia",
            "code": "SA"
        })
        state = facade.create_state({
            "name": "Riyadh",
            "country_id": country.id
        })
        city = facade.create_city({
            "name": "Riyadh",
            "state_id": state.id
        })
        place_type = facade.create_place_type({"name": "Apartment"})
        policy = facade.create_cancellation_policy({
            "name": "Flexible",
            "description": "Full refund seven days before arrival"
        })
        category = facade.create_amenity_category({"name": "Internet"})
        amenity = facade.create_amenity({
            "name": "Wi-Fi",
            "description": "High-speed wireless internet",
            "category_id": category.id
        })
        self.place = facade.create_place({
            "title": "Central Apartment",
            "description": "Apartment in central Riyadh",
            "price": 100,
            "latitude": 24.7,
            "longitude": 46.7,
            "owner_id": self.user.id,
            "business_owner_id": self.owner.id,
            "city_id": city.id,
            "place_type_id": place_type.id,
            "cancellation_policy_id": policy.id,
            "number_rooms": 2,
            "number_bathrooms": 1,
            "max_guest": 4,
            "amenities": [amenity.id]
        })

    def tearDown(self):
        """Remove all test data."""
        db.session.remove()
        db.drop_all()
        self.context.pop()

    def test_extended_entities_are_mapped_and_persistent(self):
        """Location, ownership, room, and pricing records persist."""
        room = facade.create_room_detail({
            "place_id": self.place.id,
            "room_name": "Main bedroom",
            "bed_type": "Queen",
            "beds_count": 1
        })
        pricing = facade.create_seasonal_pricing({
            "place_id": self.place.id,
            "start_date": "2026-08-10",
            "end_date": "2026-08-12",
            "special_price": 150
        })
        facade.create_place_availability({
            "place_id": self.place.id,
            "start_date": "2026-09-01",
            "end_date": "2026-09-03",
            "is_booked": True
        })

        db.session.expire_all()
        stored_owner = db.session.get(Owner, self.owner.id)
        stored_city = db.session.get(City, self.place.city_id)
        self.assertTrue(stored_owner.verify_password("owner-password"))
        self.assertEqual(stored_city.name, "Riyadh")
        self.assertEqual(room.place_id, self.place.id)
        self.assertTrue(pricing.is_active("2026-08-11"))
        self.assertEqual(
            self.place.calculate_total_price("2026-08-10", "2026-08-13"),
            450
        )

    def test_booking_review_and_notification_relationships(self):
        """Booking and review relationships persist in both directions."""
        booking = facade.create_booking({
            "place_id": self.place.id,
            "user_id": self.user.id,
            "start_date": "2026-10-01",
            "end_date": "2026-10-03"
        })
        guests = facade.create_booking_guest({
            "booking_id": booking.id,
            "adults_count": 2,
            "children_count": 1
        })
        history = facade.update_booking_status(booking.id, "confirmed")
        review = facade.create_review({
            "text": "Comfortable stay",
            "rating": 5,
            "user_id": self.user.id,
            "place_id": self.place.id
        })
        details = facade.create_review_rating_details({
            "review_id": review.id,
            "cleanliness": 5,
            "accuracy": 4,
            "communication": 5,
            "location": 4,
            "check_in": 5,
            "value": 4
        })
        response = facade.create_review_response({
            "review_id": review.id,
            "owner_id": self.owner.id,
            "response_text": "Thank you for staying with us"
        })
        guest_review = facade.create_guest_review({
            "booking_id": booking.id,
            "owner_id": self.owner.id,
            "guest_id": self.user.id,
            "cleanliness_rating": 5,
            "communication_rating": 5,
            "respect_rules_rating": 5,
            "review_text": "Respectful guest"
        })
        notification = facade.create_notification({
            "notification_type": "booking_confirmed",
            "content": "Your booking is confirmed",
            "user_id": self.user.id
        })

        db.session.expire_all()
        stored_booking = db.session.get(Booking, booking.id)
        stored_notification = db.session.get(
            SystemNotification,
            notification.id
        )
        self.assertEqual(guests.get_total_guests_count(), 3)
        self.assertEqual(stored_booking.status, "confirmed")
        self.assertEqual(history.new_status, "confirmed")
        self.assertEqual(details.calculate_average_rating(), 4.5)
        self.assertEqual(response.review_id, review.id)
        self.assertEqual(guest_review.guest_id, self.user.id)
        stored_notification.mark_as_read()
        db.session.commit()
        self.assertTrue(stored_notification.is_seen)


if __name__ == "__main__":
    unittest.main()
