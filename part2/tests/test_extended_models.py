#!/usr/bin/python3
"""Tests for the extended Part 1 business design in Part 2."""

import unittest

from app.services.facade import HBnBFacade


class TestExtendedBusinessModels(unittest.TestCase):
    """Exercise the extended entities and their relationships."""

    def setUp(self):
        """Create one connected place and its supporting records."""
        self.facade = HBnBFacade()
        self.user = self.facade.create_user({
            "first_name": "Sara",
            "last_name": "Guest",
            "email": "sara@example.com"
        })
        self.owner = self.facade.create_owner({
            "business_name": "Riyadh Stays",
            "contact_person": "Nora Owner",
            "email": "owner@example.com",
            "password": "owner-password",
            "phone_number": "+966500000000",
            "commercial_register": "CR-1000"
        })
        country = self.facade.create_country({
            "name": "Saudi Arabia",
            "code": "SA"
        })
        state = self.facade.create_state({
            "name": "Riyadh",
            "country_id": country.id
        })
        city = self.facade.create_city({
            "name": "Riyadh",
            "state_id": state.id
        })
        place_type = self.facade.create_place_type({"name": "Apartment"})
        policy = self.facade.create_cancellation_policy({
            "name": "Flexible",
            "description": "Full refund seven days before arrival"
        })
        category = self.facade.create_amenity_category({"name": "Internet"})
        amenity = self.facade.create_amenity({
            "name": "Wi-Fi",
            "description": "High-speed wireless internet",
            "category_id": category.id
        })
        self.place = self.facade.create_place({
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

    def test_place_supporting_entities_and_pricing(self):
        """Place details, availability, and pricing work together."""
        room = self.facade.create_room_detail({
            "place_id": self.place.id,
            "room_name": "Main bedroom",
            "bed_type": "Queen",
            "beds_count": 1
        })
        pricing = self.facade.create_seasonal_pricing({
            "place_id": self.place.id,
            "start_date": "2026-08-10",
            "end_date": "2026-08-12",
            "special_price": 150
        })
        self.facade.create_place_availability({
            "place_id": self.place.id,
            "start_date": "2026-09-01",
            "end_date": "2026-09-03",
            "is_booked": True
        })

        self.assertEqual(room.place, self.place)
        self.assertTrue(pricing.is_active("2026-08-10"))
        self.assertEqual(
            self.place.calculate_total_price("2026-08-10", "2026-08-13"),
            450
        )
        self.assertFalse(
            self.place.check_availability("2026-09-01", "2026-09-02")
        )

    def test_booking_reviews_and_notifications(self):
        """Bookings, reviews, owner responses, and notifications connect."""
        booking = self.facade.create_booking({
            "place_id": self.place.id,
            "user_id": self.user.id,
            "start_date": "2026-10-01",
            "end_date": "2026-10-03"
        })
        guests = self.facade.create_booking_guest({
            "booking_id": booking.id,
            "adults_count": 2,
            "children_count": 1
        })
        self.facade.update_booking_status(booking.id, "confirmed")
        review = self.facade.create_review({
            "text": "Comfortable stay",
            "rating": 5,
            "user_id": self.user.id,
            "place_id": self.place.id
        })
        details = self.facade.create_review_rating_details({
            "review_id": review.id,
            "cleanliness": 5,
            "accuracy": 4,
            "communication": 5,
            "location": 4,
            "check_in": 5,
            "value": 4
        })
        response = self.facade.create_review_response({
            "review_id": review.id,
            "owner_id": self.owner.id,
            "response_text": "Thank you for staying with us"
        })
        guest_review = self.facade.create_guest_review({
            "booking_id": booking.id,
            "owner_id": self.owner.id,
            "guest_id": self.user.id,
            "cleanliness_rating": 5,
            "communication_rating": 5,
            "respect_rules_rating": 5,
            "review_text": "Respectful guest"
        })
        notification = self.facade.create_notification({
            "notification_type": "booking_confirmed",
            "content": "Your booking is confirmed",
            "user_id": self.user.id
        })

        self.assertEqual(guests.get_total_guests_count(), 3)
        self.assertEqual(booking.status, "confirmed")
        self.assertEqual(booking.history[-1].new_status, "confirmed")
        self.assertEqual(details.calculate_average_rating(), 4.5)
        self.assertIs(review.response, response)
        self.assertIn(guest_review, self.user.guest_reviews)
        notification.mark_as_read()
        self.assertTrue(notification.is_seen)


if __name__ == "__main__":
    unittest.main()
