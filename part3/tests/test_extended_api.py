#!/usr/bin/python3
"""Integration tests for authenticated extended HBnB endpoints."""

import unittest

from app import create_app, db
from app.services import facade


class TestConfig:
    """Use an isolated SQLite database."""

    TESTING = True
    SECRET_KEY = "test-secret"
    JWT_SECRET_KEY = "test-jwt-secret-with-at-least-32-characters"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class TestExtendedAPI(unittest.TestCase):
    """Validate persistence and authorization for extended entities."""

    def setUp(self):
        """Create a clean database and users for each access level."""
        self.app = create_app(TestConfig)
        self.context = self.app.app_context()
        self.context.push()
        db.create_all()
        self.client = self.app.test_client()

        facade.create_user({
            "first_name": "Admin",
            "last_name": "User",
            "email": "admin@example.com",
            "password": "adminpass",
            "is_admin": True
        })
        facade.create_user({
            "first_name": "Host",
            "last_name": "User",
            "email": "host@example.com",
            "password": "hostpass"
        })
        self.guest = facade.create_user({
            "first_name": "Guest",
            "last_name": "User",
            "email": "guest@example.com",
            "password": "guestpass"
        })
        self.admin_headers = self.login("admin@example.com", "adminpass")
        self.host_headers = self.login("host@example.com", "hostpass")
        self.guest_headers = self.login("guest@example.com", "guestpass")

    def tearDown(self):
        """Remove test records and the application context."""
        db.session.remove()
        db.drop_all()
        self.context.pop()

    def login(self, email, password):
        """Return an Authorization header for a user."""
        response = self.client.post("/api/v1/auth/login", json={
            "email": email,
            "password": password
        })
        self.assertEqual(response.status_code, 200)
        token = response.get_json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    def post(self, path, data, headers):
        """Post JSON and return a successful creation response."""
        response = self.client.post(path, json=data, headers=headers)
        self.assertEqual(response.status_code, 201, response.get_json())
        return response.get_json()

    def test_extended_entities_persist_with_authorization(self):
        """Create and connect all extended entities through protected APIs."""
        owner = self.post("/api/v1/owners/", {
            "business_name": "Stay Co",
            "contact_person": "Mona",
            "email": "owner@example.com",
            "password": "secret",
            "phone_number": "0500000000",
            "commercial_register": "CR-1"
        }, self.admin_headers)
        country = self.post("/api/v1/countries/", {
            "name": "Saudi Arabia",
            "code": "SA"
        }, self.admin_headers)
        state = self.post("/api/v1/states/", {
            "name": "Riyadh",
            "country_id": country["id"]
        }, self.admin_headers)
        city = self.post("/api/v1/cities/", {
            "name": "Riyadh",
            "state_id": state["id"]
        }, self.admin_headers)
        place_type = self.post("/api/v1/place-types/", {
            "name": "Apartment"
        }, self.admin_headers)
        policy = self.post("/api/v1/cancellation-policies/", {
            "name": "Flexible",
            "description": "Full refund before seven days"
        }, self.admin_headers)
        category = self.post("/api/v1/amenity-categories/", {
            "name": "Essentials"
        }, self.admin_headers)
        amenity = self.post("/api/v1/amenities/", {
            "name": "WiFi",
            "description": "Fast internet",
            "category_id": category["id"]
        }, self.admin_headers)
        place = self.post("/api/v1/places/", {
            "title": "City Home",
            "description": "Central",
            "price": 100,
            "latitude": 24.7,
            "longitude": 46.7,
            "amenities": [amenity["id"]],
            "city_id": city["id"],
            "place_type_id": place_type["id"],
            "cancellation_policy_id": policy["id"],
            "business_owner_id": owner["id"],
            "number_rooms": 2,
            "number_bathrooms": 1,
            "max_guest": 4
        }, self.host_headers)
        room = self.post("/api/v1/room-details/", {
            "place_id": place["id"],
            "room_name": "Main room",
            "bed_type": "Queen",
            "beds_count": 1
        }, self.host_headers)
        availability = self.post("/api/v1/place-availability/", {
            "place_id": place["id"],
            "start_date": "2026-09-01",
            "end_date": "2026-09-30"
        }, self.host_headers)
        pricing = self.post("/api/v1/seasonal-pricing/", {
            "place_id": place["id"],
            "start_date": "2026-09-10",
            "end_date": "2026-09-15",
            "special_price": 150
        }, self.host_headers)
        booking = self.post("/api/v1/bookings/", {
            "place_id": place["id"],
            "start_date": "2026-09-02",
            "end_date": "2026-09-04"
        }, self.guest_headers)
        self.assertEqual(booking["user_id"], self.guest.id)
        self.post("/api/v1/booking-guests/", {
            "booking_id": booking["id"],
            "adults_count": 2
        }, self.guest_headers)
        review = self.post("/api/v1/reviews/", {
            "text": "Great",
            "rating": 5,
            "place_id": place["id"]
        }, self.guest_headers)
        self.post("/api/v1/review-ratings/", {
            "review_id": review["id"],
            "cleanliness": 5,
            "accuracy": 5,
            "communication": 4,
            "location": 5,
            "check_in": 4,
            "value": 5
        }, self.guest_headers)
        self.post("/api/v1/review-responses/", {
            "review_id": review["id"],
            "owner_id": owner["id"],
            "response_text": "Thank you"
        }, self.admin_headers)
        self.post("/api/v1/guest-reviews/", {
            "booking_id": booking["id"],
            "owner_id": owner["id"],
            "guest_id": self.guest.id,
            "cleanliness_rating": 5,
            "communication_rating": 5,
            "respect_rules_rating": 5,
            "review_text": "Excellent guest"
        }, self.admin_headers)
        notification = self.post("/api/v1/notifications/", {
            "notification_type": "booking",
            "content": "Booking created",
            "user_id": self.guest.id
        }, self.admin_headers)

        response = self.client.put(
            f"/api/v1/bookings/{booking['id']}",
            json={"status": "confirmed"},
            headers=self.guest_headers
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["status"], "confirmed")

        response = self.client.put(
            f"/api/v1/notifications/{notification['id']}/read",
            headers=self.guest_headers
        )
        self.assertTrue(response.get_json()["is_seen"])

        response = self.client.put(
            f"/api/v1/room-details/{room['id']}",
            json={"beds_count": 2},
            headers=self.guest_headers
        )
        self.assertEqual(response.status_code, 403)

        details = self.client.get(
            f"/api/v1/places/{place['id']}"
        ).get_json()
        self.assertIn(room["id"], details["room_detail_ids"])
        self.assertIn(availability["id"], details["availability_ids"])
        self.assertIn(pricing["id"], details["seasonal_pricing_ids"])

    def test_reference_writes_require_admin(self):
        """Block regular users from changing reference data."""
        response = self.client.post(
            "/api/v1/countries/",
            json={"name": "Saudi Arabia", "code": "SA"},
            headers=self.host_headers
        )
        self.assertEqual(response.status_code, 403)

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
