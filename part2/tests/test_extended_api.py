#!/usr/bin/python3
"""Integration tests for the API built from the extended Part 1 design."""

import unittest

from app import create_app


class TestExtendedAPI(unittest.TestCase):
    """Validate that every extended entity is available through the API."""

    def setUp(self):
        """Create a clean in-memory application."""
        self.app = create_app()
        self.client = self.app.test_client()

    def post(self, path, data):
        """Post JSON and return a successful creation response."""
        response = self.client.post(path, json=data)
        self.assertEqual(response.status_code, 201, response.get_json())
        return response.get_json()

    def test_extended_entities_work_together(self):
        """Create and connect all entities added by the Part 1 design."""
        user = self.post("/api/v1/users/", {
            "first_name": "Sara",
            "last_name": "Ali",
            "email": "sara@example.com"
        })
        owner = self.post("/api/v1/owners/", {
            "business_name": "Stay Co",
            "contact_person": "Mona",
            "email": "owner@example.com",
            "password": "secret",
            "phone_number": "0500000000",
            "commercial_register": "CR-1"
        })
        country = self.post("/api/v1/countries/", {
            "name": "Saudi Arabia",
            "code": "SA"
        })
        state = self.post("/api/v1/states/", {
            "name": "Riyadh",
            "country_id": country["id"]
        })
        city = self.post("/api/v1/cities/", {
            "name": "Riyadh",
            "state_id": state["id"]
        })
        place_type = self.post("/api/v1/place-types/", {
            "name": "Apartment"
        })
        policy = self.post("/api/v1/cancellation-policies/", {
            "name": "Flexible",
            "description": "Full refund before seven days"
        })
        category = self.post("/api/v1/amenity-categories/", {
            "name": "Essentials"
        })
        amenity = self.post("/api/v1/amenities/", {
            "name": "WiFi",
            "description": "Fast internet",
            "category_id": category["id"]
        })
        place = self.post("/api/v1/places/", {
            "title": "City Home",
            "description": "Central",
            "price": 100,
            "latitude": 24.7,
            "longitude": 46.7,
            "owner_id": user["id"],
            "amenities": [amenity["id"]],
            "city_id": city["id"],
            "place_type_id": place_type["id"],
            "cancellation_policy_id": policy["id"],
            "business_owner_id": owner["id"],
            "number_rooms": 2,
            "number_bathrooms": 1,
            "max_guest": 4
        })
        room = self.post("/api/v1/room-details/", {
            "place_id": place["id"],
            "room_name": "Main room",
            "bed_type": "Queen",
            "beds_count": 1
        })
        availability = self.post("/api/v1/place-availability/", {
            "place_id": place["id"],
            "start_date": "2026-09-01",
            "end_date": "2026-09-30"
        })
        pricing = self.post("/api/v1/seasonal-pricing/", {
            "place_id": place["id"],
            "start_date": "2026-09-10",
            "end_date": "2026-09-15",
            "special_price": 150
        })
        booking = self.post("/api/v1/bookings/", {
            "place_id": place["id"],
            "user_id": user["id"],
            "start_date": "2026-09-02",
            "end_date": "2026-09-04"
        })
        self.post("/api/v1/booking-guests/", {
            "booking_id": booking["id"],
            "adults_count": 2,
            "children_count": 1
        })
        review = self.post("/api/v1/reviews/", {
            "text": "Great",
            "rating": 5,
            "user_id": user["id"],
            "place_id": place["id"]
        })
        self.post("/api/v1/review-ratings/", {
            "review_id": review["id"],
            "cleanliness": 5,
            "accuracy": 5,
            "communication": 4,
            "location": 5,
            "check_in": 4,
            "value": 5
        })
        self.post("/api/v1/review-responses/", {
            "review_id": review["id"],
            "owner_id": owner["id"],
            "response_text": "Thank you"
        })
        self.post("/api/v1/guest-reviews/", {
            "booking_id": booking["id"],
            "owner_id": owner["id"],
            "guest_id": user["id"],
            "cleanliness_rating": 5,
            "communication_rating": 5,
            "respect_rules_rating": 5,
            "review_text": "Excellent guest"
        })
        notification = self.post("/api/v1/notifications/", {
            "notification_type": "booking",
            "content": "Booking created",
            "user_id": user["id"]
        })

        response = self.client.put(
            f"/api/v1/bookings/{booking['id']}",
            json={"status": "confirmed"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["status"], "confirmed")

        response = self.client.put(
            f"/api/v1/notifications/{notification['id']}/read"
        )
        self.assertTrue(response.get_json()["is_seen"])

        details = self.client.get(
            f"/api/v1/places/{place['id']}"
        ).get_json()
        self.assertIn(room["id"], details["room_detail_ids"])
        self.assertIn(availability["id"], details["availability_ids"])
        self.assertIn(pricing["id"], details["seasonal_pricing_ids"])

    def test_swagger_lists_extended_routes(self):
        """Document every extended resource in Swagger."""
        paths = self.client.get("/swagger.json").get_json()["paths"]
        expected = {
            "/api/v1/owners/",
            "/api/v1/countries/",
            "/api/v1/states/",
            "/api/v1/cities/",
            "/api/v1/place-types/",
            "/api/v1/cancellation-policies/",
            "/api/v1/amenity-categories/",
            "/api/v1/room-details/",
            "/api/v1/place-availability/",
            "/api/v1/seasonal-pricing/",
            "/api/v1/bookings/",
            "/api/v1/booking-guests/",
            "/api/v1/booking-history/",
            "/api/v1/review-ratings/",
            "/api/v1/review-responses/",
            "/api/v1/guest-reviews/",
            "/api/v1/notifications/"
        }
        self.assertTrue(expected.issubset(paths))


if __name__ == "__main__":
    unittest.main()
