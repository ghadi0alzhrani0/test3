#!/usr/bin/python3
"""Unit tests for HBnB Part 2 endpoints."""

import time
import unittest

from app import create_app
from app.persistence.repository import InMemoryRepository
from app.services.facade import HBnBFacade


class TestHBnBEndpoints(unittest.TestCase):
    """Validate the core Part 2 API behavior."""

    def setUp(self):
        """Create a fresh test client for each test."""
        self.app = create_app()
        self.client = self.app.test_client()

    def create_user(self):
        """Create a reusable test user."""
        response = self.client.post("/api/v1/users/", json={
            "first_name": "Jane",
            "last_name": "Doe",
            "email": "jane.doe@example.com"
        })
        self.assertEqual(response.status_code, 201)
        return response.get_json()

    def create_amenity(self):
        """Create a reusable test amenity."""
        response = self.client.post("/api/v1/amenities/", json={
            "name": "Wi-Fi"
        })
        self.assertEqual(response.status_code, 201)
        return response.get_json()

    def create_place(self):
        """Create a reusable test place."""
        user = self.create_user()
        amenity = self.create_amenity()
        response = self.client.post("/api/v1/places/", json={
            "title": "Cozy Apartment",
            "description": "A nice place to stay",
            "price": 100.0,
            "latitude": 37.7749,
            "longitude": -122.4194,
            "owner_id": user["id"],
            "amenities": [amenity["id"]]
        })
        self.assertEqual(response.status_code, 201)
        return response.get_json()

    def create_review(self):
        """Create a reusable test review."""
        place = self.create_place()
        users = self.client.get("/api/v1/users/").get_json()
        response = self.client.post("/api/v1/reviews/", json={
            "text": "Great stay!",
            "rating": 5,
            "user_id": users[0]["id"],
            "place_id": place["id"]
        })
        self.assertEqual(response.status_code, 201)
        return response.get_json()

    def test_facade_uses_in_memory_repositories(self):
        """The facade keeps one repository for each main entity."""
        facade = HBnBFacade()
        repositories = (
            facade.user_repo,
            facade.place_repo,
            facade.review_repo,
            facade.amenity_repo
        )

        for repository in repositories:
            self.assertIsInstance(repository, InMemoryRepository)

    def test_create_user_and_retrieve_list(self):
        """Users can be created and listed."""
        user = self.create_user()
        response = self.client.get("/api/v1/users/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()[0]["id"], user["id"])
        self.assertNotIn("password", response.get_json()[0])

    def test_get_and_update_user(self):
        """A user can be retrieved and updated by ID."""
        user = self.create_user()

        response = self.client.get(f"/api/v1/users/{user['id']}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["email"], user["email"])

        response = self.client.put(
            f"/api/v1/users/{user['id']}",
            json={
                "first_name": "Janet",
                "last_name": "Doe",
                "email": "janet.doe@example.com"
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["first_name"], "Janet")

    def test_create_user_invalid_data(self):
        """Invalid user payloads are rejected."""
        response = self.client.post("/api/v1/users/", json={
            "first_name": "",
            "last_name": "",
            "email": "not-an-email"
        })

        self.assertEqual(response.status_code, 400)

    def test_duplicate_user_email_is_rejected(self):
        """User emails must remain unique and case-insensitive."""
        self.create_user()
        response = self.client.post("/api/v1/users/", json={
            "first_name": "Another",
            "last_name": "User",
            "email": "JANE.DOE@EXAMPLE.COM"
        })
        self.assertEqual(response.status_code, 400)

    def test_missing_user_returns_not_found(self):
        """Unknown user IDs return 404 for GET and PUT."""
        response = self.client.get("/api/v1/users/missing")
        self.assertEqual(response.status_code, 404)

        response = self.client.put("/api/v1/users/missing", json={
            "first_name": "Jane",
            "last_name": "Doe",
            "email": "jane.doe@example.com"
        })
        self.assertEqual(response.status_code, 404)

    def test_amenity_crud_without_delete(self):
        """Amenities can be created, read, listed, and updated."""
        amenity = self.create_amenity()

        response = self.client.get(f"/api/v1/amenities/{amenity['id']}")
        self.assertEqual(response.status_code, 200)

        response = self.client.put(
            f"/api/v1/amenities/{amenity['id']}",
            json={"name": "Air Conditioning"}
        )
        self.assertEqual(response.status_code, 200)

        response = self.client.get("/api/v1/amenities/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.get_json()), 1)

    def test_invalid_and_missing_amenity(self):
        """Invalid amenity data and unknown IDs are rejected."""
        response = self.client.post("/api/v1/amenities/", json={
            "name": "   "
        })
        self.assertEqual(response.status_code, 400)

        response = self.client.get("/api/v1/amenities/missing")
        self.assertEqual(response.status_code, 404)

        response = self.client.put(
            "/api/v1/amenities/missing",
            json={"name": "Pool"}
        )
        self.assertEqual(response.status_code, 404)

    def test_place_with_owner_and_amenity(self):
        """Places include owner and amenity relationships."""
        place = self.create_place()
        response = self.client.get(f"/api/v1/places/{place['id']}")

        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["owner"]["email"], "jane.doe@example.com")
        self.assertEqual(data["amenities"][0]["name"], "Wi-Fi")

        response = self.client.get("/api/v1/places/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()[0]["id"], place["id"])

    def test_update_place(self):
        """A place can be partially updated."""
        place = self.create_place()
        old_updated_at = place["updated_at"]
        time.sleep(0.001)
        response = self.client.put(
            f"/api/v1/places/{place['id']}",
            json={"title": "Updated Apartment", "price": 125.0}
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["title"], "Updated Apartment")
        self.assertEqual(data["price"], 125.0)
        self.assertNotEqual(data["updated_at"], old_updated_at)

    def test_place_description_is_optional(self):
        """A place can be created without a description."""
        user = self.create_user()
        response = self.client.post("/api/v1/places/", json={
            "title": "Simple Room",
            "price": 75.0,
            "latitude": 24.7,
            "longitude": 46.7,
            "owner_id": user["id"],
            "amenities": []
        })

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_json()["description"], "")

    def test_place_validation_boundaries(self):
        """Invalid price and coordinates are rejected."""
        user = self.create_user()
        base_data = {
            "title": "Boundary Place",
            "description": "Validation test",
            "price": 50.0,
            "latitude": 24.7,
            "longitude": 46.7,
            "owner_id": user["id"],
            "amenities": []
        }
        invalid_values = (
            ("price", -1),
            ("latitude", -90.1),
            ("latitude", 90.1),
            ("longitude", -180.1),
            ("longitude", 180.1)
        )

        for field, value in invalid_values:
            with self.subTest(field=field, value=value):
                data = base_data.copy()
                data[field] = value
                response = self.client.post("/api/v1/places/", json=data)
                self.assertEqual(response.status_code, 400)

    def test_place_relationships_must_exist(self):
        """Place owners and amenities must reference stored entities."""
        user = self.create_user()
        data = {
            "title": "Relationship Place",
            "description": "Validation test",
            "price": 50.0,
            "latitude": 24.7,
            "longitude": 46.7,
            "owner_id": "missing",
            "amenities": []
        }
        response = self.client.post("/api/v1/places/", json=data)
        self.assertEqual(response.status_code, 400)

        data["owner_id"] = user["id"]
        data["amenities"] = ["missing"]
        response = self.client.post("/api/v1/places/", json=data)
        self.assertEqual(response.status_code, 400)

    def test_missing_place_returns_not_found(self):
        """Unknown place IDs return 404."""
        response = self.client.get("/api/v1/places/missing")
        self.assertEqual(response.status_code, 404)

        response = self.client.put(
            "/api/v1/places/missing",
            json={"title": "Missing Place"}
        )
        self.assertEqual(response.status_code, 404)

        response = self.client.get("/api/v1/places/missing/reviews")
        self.assertEqual(response.status_code, 404)

    def test_review_create_update_delete(self):
        """Reviews can be created, retrieved by place, updated, and deleted."""
        review = self.create_review()

        response = self.client.get(f"/api/v1/reviews/{review['id']}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["place_id"], review["place_id"])

        response = self.client.get("/api/v1/reviews/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()[0]["id"], review["id"])

        time.sleep(0.001)
        response = self.client.put(
            f"/api/v1/reviews/{review['id']}",
            json={"text": "Amazing stay!", "rating": 4}
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["text"], "Amazing stay!")
        self.assertEqual(data["rating"], 4)
        self.assertNotEqual(data["updated_at"], review["updated_at"])

        response = self.client.delete(f"/api/v1/reviews/{review['id']}")
        self.assertEqual(response.status_code, 200)

        response = self.client.get(
            f"/api/v1/places/{review['place_id']}/reviews"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), [])

    def test_review_validation(self):
        """Review text, rating, user, and place are validated."""
        place = self.create_place()
        user = self.client.get("/api/v1/users/").get_json()[0]
        base_data = {
            "text": "Good stay",
            "rating": 5,
            "user_id": user["id"],
            "place_id": place["id"]
        }
        invalid_data = (
            {**base_data, "text": "   "},
            {**base_data, "rating": 0},
            {**base_data, "rating": 6},
            {**base_data, "user_id": "missing"},
            {**base_data, "place_id": "missing"}
        )

        for data in invalid_data:
            with self.subTest(data=data):
                response = self.client.post("/api/v1/reviews/", json=data)
                self.assertEqual(response.status_code, 400)

    def test_missing_review_returns_not_found(self):
        """Unknown review IDs return 404 for GET, PUT, and DELETE."""
        response = self.client.get("/api/v1/reviews/missing")
        self.assertEqual(response.status_code, 404)

        response = self.client.put(
            "/api/v1/reviews/missing",
            json={"text": "Updated", "rating": 4}
        )
        self.assertEqual(response.status_code, 404)

        response = self.client.delete("/api/v1/reviews/missing")
        self.assertEqual(response.status_code, 404)

    def test_swagger_documentation_is_available(self):
        """Swagger documentation describes the required API routes."""
        response = self.client.get("/api/v1/")
        self.assertEqual(response.status_code, 200)

        response = self.client.get("/swagger.json")
        self.assertEqual(response.status_code, 200)
        paths = response.get_json()["paths"]
        expected_paths = (
            "/api/v1/users/",
            "/api/v1/users/{user_id}",
            "/api/v1/amenities/",
            "/api/v1/amenities/{amenity_id}",
            "/api/v1/places/",
            "/api/v1/places/{place_id}",
            "/api/v1/places/{place_id}/reviews",
            "/api/v1/reviews/",
            "/api/v1/reviews/{review_id}"
        )
        for path in expected_paths:
            with self.subTest(path=path):
                self.assertIn(path, paths)


if __name__ == "__main__":
    unittest.main()
