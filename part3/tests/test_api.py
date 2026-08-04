#!/usr/bin/python3
"""Unit tests for HBnB Part 3 authentication and persistence."""

import unittest

from app import create_app, db
from app.services import facade


class TestConfig:
    """Use a separate in-memory database for tests."""

    TESTING = True
    SECRET_KEY = "test-secret-key"
    JWT_SECRET_KEY = "test-jwt-secret-key-with-32-characters"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class TestHBnBPart3(unittest.TestCase):
    """Validate authentication, authorization, and SQL persistence."""

    def setUp(self):
        """Create a clean database and test client."""
        self.app = create_app(TestConfig)
        self.context = self.app.app_context()
        self.context.push()
        db.create_all()
        self.client = self.app.test_client()

    def tearDown(self):
        """Remove all test data."""
        db.session.remove()
        db.drop_all()
        self.context.pop()

    def create_user(
        self,
        email="jane.doe@example.com",
        password="secret123",
        is_admin=False
    ):
        """Create a user through the service layer."""
        user = facade.create_user({
            "first_name": "Jane",
            "last_name": "Doe",
            "email": email,
            "password": password,
            "is_admin": is_admin
        })
        return user.id

    def login(self, email="jane.doe@example.com", password="secret123"):
        """Log in and return an Authorization header."""
        response = self.client.post("/api/v1/auth/login", json={
            "email": email,
            "password": password
        })
        self.assertEqual(response.status_code, 200)
        token = response.get_json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    def create_admin(self):
        """Create an administrator and return an Authorization header."""
        self.create_user(
            email="admin@example.com",
            password="admin1234",
            is_admin=True
        )
        return self.login("admin@example.com", "admin1234")

    def create_place(self, headers, title="Cozy Apartment"):
        """Create a place through the protected endpoint."""
        response = self.client.post(
            "/api/v1/places/",
            json={
                "title": title,
                "description": "A nice place to stay",
                "price": 100.0,
                "latitude": 37.7749,
                "longitude": -122.4194,
                "amenities": []
            },
            headers=headers
        )
        self.assertEqual(response.status_code, 201)
        return response.get_json()

    def create_review(self, headers, place_id):
        """Create a review through the protected endpoint."""
        response = self.client.post(
            "/api/v1/reviews/",
            json={
                "text": "Great stay",
                "rating": 5,
                "place_id": place_id
            },
            headers=headers
        )
        self.assertEqual(response.status_code, 201)
        return response.get_json()

    def test_password_is_hashed_and_hidden(self):
        """Passwords are hashed and never returned by GET endpoints."""
        user_id = self.create_user()
        user = facade.get_user(user_id)

        self.assertNotEqual(user.password, "secret123")
        self.assertTrue(user.verify_password("secret123"))
        self.assertFalse(user.verify_password("wrong-password"))

        response = self.client.get(f"/api/v1/users/{user_id}")
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("password", response.get_json())

        response = self.client.get("/api/v1/users/")
        self.assertNotIn("password", response.get_json()[0])

    def test_login_accepts_only_valid_credentials(self):
        """Valid credentials return a token and invalid ones return 401."""
        self.create_user()
        response = self.client.post("/api/v1/auth/login", json={
            "email": "jane.doe@example.com",
            "password": "secret123"
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn("access_token", response.get_json())

        response = self.client.post("/api/v1/auth/login", json={
            "email": "jane.doe@example.com",
            "password": "wrong-password"
        })
        self.assertEqual(response.status_code, 401)

    def test_protected_endpoint_requires_a_valid_token(self):
        """The protected endpoint returns the authenticated user ID."""
        user_id = self.create_user()

        response = self.client.get("/api/v1/protected")
        self.assertEqual(response.status_code, 401)

        response = self.client.get(
            "/api/v1/protected",
            headers=self.login()
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get_json()["message"],
            f"Hello, user {user_id}"
        )

    def test_only_admin_can_create_users(self):
        """The user creation endpoint is restricted to administrators."""
        data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@example.com",
            "password": "password123"
        }

        response = self.client.post("/api/v1/users/", json=data)
        self.assertEqual(response.status_code, 401)

        self.create_user()
        response = self.client.post(
            "/api/v1/users/",
            json=data,
            headers=self.login()
        )
        self.assertEqual(response.status_code, 403)

        response = self.client.post(
            "/api/v1/users/",
            json=data,
            headers=self.create_admin()
        )
        self.assertEqual(response.status_code, 201)
        self.assertNotIn("password", response.get_json())

    def test_admin_can_update_any_user_login_data(self):
        """Admins can change another user's email and password."""
        user_id = self.create_user()
        admin_headers = self.create_admin()

        response = self.client.put(
            f"/api/v1/users/{user_id}",
            json={
                "email": "updated@example.com",
                "password": "new-password"
            },
            headers=admin_headers
        )
        self.assertEqual(response.status_code, 200)

        response = self.client.post("/api/v1/auth/login", json={
            "email": "updated@example.com",
            "password": "new-password"
        })
        self.assertEqual(response.status_code, 200)

    def test_admin_cannot_duplicate_an_email(self):
        """Admin updates preserve the unique email constraint."""
        first_id = self.create_user()
        self.create_user(
            email="second@example.com",
            password="second-password"
        )

        response = self.client.put(
            f"/api/v1/users/{first_id}",
            json={"email": "second@example.com"},
            headers=self.create_admin()
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.get_json()["error"],
            "Email already in use"
        )

    def test_regular_user_can_only_update_own_name(self):
        """Users cannot update another profile or their login fields."""
        user_id = self.create_user()
        headers = self.login()
        other_id = self.create_user(
            email="other@example.com",
            password="other-password"
        )

        response = self.client.put(
            f"/api/v1/users/{user_id}",
            json={"first_name": "Janet"},
            headers=headers
        )
        self.assertEqual(response.status_code, 200)

        response = self.client.put(
            f"/api/v1/users/{other_id}",
            json={"first_name": "Changed"},
            headers=headers
        )
        self.assertEqual(response.status_code, 403)

        response = self.client.put(
            f"/api/v1/users/{user_id}",
            json={"password": "changed"},
            headers=headers
        )
        self.assertEqual(response.status_code, 400)

        response = self.client.put(
            f"/api/v1/users/{user_id}",
            json={"is_admin": True},
            headers=headers
        )
        self.assertEqual(response.status_code, 403)

    def test_only_admin_can_manage_amenities(self):
        """Amenity creation and modification require admin privileges."""
        self.create_user()
        user_headers = self.login()

        response = self.client.post(
            "/api/v1/amenities/",
            json={"name": "WiFi"},
            headers=user_headers
        )
        self.assertEqual(response.status_code, 403)

        admin_headers = self.create_admin()
        response = self.client.post(
            "/api/v1/amenities/",
            json={"name": "WiFi"},
            headers=admin_headers
        )
        self.assertEqual(response.status_code, 201)
        amenity = response.get_json()
        amenity_id = amenity["id"]

        response = self.client.put(
            f"/api/v1/amenities/{amenity_id}",
            json={"name": "Fast WiFi"},
            headers=admin_headers
        )
        self.assertEqual(response.status_code, 200)
        updated = response.get_json()
        self.assertEqual(updated["id"], amenity_id)
        self.assertEqual(updated["name"], "Fast WiFi")
        self.assertNotEqual(updated["updated_at"], amenity["updated_at"])

    def test_place_owner_is_taken_from_token(self):
        """A new place belongs to the authenticated user."""
        user_id = self.create_user()
        place = self.create_place(self.login())

        response = self.client.get(f"/api/v1/places/{place['id']}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["owner"]["id"], user_id)

    def test_place_get_endpoints_are_public(self):
        """Place list and detail endpoints do not require a token."""
        self.create_user()
        place = self.create_place(self.login())

        response = self.client.get("/api/v1/places/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()[0]["price"], 100.0)

        response = self.client.get(f"/api/v1/places/{place['id']}")
        self.assertEqual(response.status_code, 200)

    def test_only_owner_or_admin_can_modify_place(self):
        """Owners and admins can update or delete a place."""
        self.create_user()
        owner_headers = self.login()
        place = self.create_place(owner_headers)

        self.create_user(
            email="other@example.com",
            password="other-password"
        )
        other_headers = self.login(
            "other@example.com",
            "other-password"
        )
        response = self.client.put(
            f"/api/v1/places/{place['id']}",
            json={"title": "Changed"},
            headers=other_headers
        )
        self.assertEqual(response.status_code, 403)

        response = self.client.put(
            f"/api/v1/places/{place['id']}",
            json={"title": "Admin Updated"},
            headers=self.create_admin()
        )
        self.assertEqual(response.status_code, 200)
        updated = response.get_json()
        self.assertEqual(updated["id"], place["id"])
        self.assertEqual(updated["title"], "Admin Updated")
        self.assertNotEqual(updated["updated_at"], place["updated_at"])

        response = self.client.delete(
            f"/api/v1/places/{place['id']}",
            headers=owner_headers
        )
        self.assertEqual(response.status_code, 200)

    def test_user_cannot_review_own_place(self):
        """Regular users cannot review their own places."""
        self.create_user()
        headers = self.login()
        place = self.create_place(headers)

        response = self.client.post(
            "/api/v1/reviews/",
            json={
                "text": "My own place",
                "rating": 5,
                "place_id": place["id"]
            },
            headers=headers
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.get_json()["error"],
            "You cannot review your own place"
        )

    def test_user_cannot_review_place_twice(self):
        """The API and database allow one review per user and place."""
        self.create_user()
        place = self.create_place(self.login())
        self.create_user(
            email="reviewer@example.com",
            password="review-password"
        )
        reviewer_headers = self.login(
            "reviewer@example.com",
            "review-password"
        )

        self.create_review(reviewer_headers, place["id"])
        response = self.client.post(
            "/api/v1/reviews/",
            json={
                "text": "Second review",
                "rating": 4,
                "place_id": place["id"]
            },
            headers=reviewer_headers
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.get_json()["error"],
            "You have already reviewed this place"
        )

    def test_only_author_or_admin_can_modify_review(self):
        """Review changes require authorship or admin privileges."""
        self.create_user()
        place = self.create_place(self.login())
        self.create_user(
            email="reviewer@example.com",
            password="review-password"
        )
        reviewer_headers = self.login(
            "reviewer@example.com",
            "review-password"
        )
        review = self.create_review(reviewer_headers, place["id"])

        response = self.client.put(
            f"/api/v1/reviews/{review['id']}",
            json={"text": "Unauthorized change"},
            headers=self.login()
        )
        self.assertEqual(response.status_code, 403)

        response = self.client.put(
            f"/api/v1/reviews/{review['id']}",
            json={"text": "Admin change"},
            headers=self.create_admin()
        )
        self.assertEqual(response.status_code, 200)
        updated = response.get_json()
        self.assertEqual(updated["id"], review["id"])
        self.assertEqual(updated["text"], "Admin change")
        self.assertNotEqual(updated["updated_at"], review["updated_at"])

        response = self.client.delete(
            f"/api/v1/reviews/{review['id']}",
            headers=reviewer_headers
        )
        self.assertEqual(response.status_code, 200)

    def test_database_relationships_are_bidirectional(self):
        """SQLAlchemy links users, places, reviews, and amenities."""
        owner_id = self.create_user()
        owner_headers = self.login()
        admin_headers = self.create_admin()

        amenity_response = self.client.post(
            "/api/v1/amenities/",
            json={"name": "Pool"},
            headers=admin_headers
        )
        amenity_id = amenity_response.get_json()["id"]

        response = self.client.post(
            "/api/v1/places/",
            json={
                "title": "Pool House",
                "description": "A place with a pool",
                "price": 200,
                "latitude": 24.7,
                "longitude": 46.7,
                "amenities": [amenity_id]
            },
            headers=owner_headers
        )
        place_id = response.get_json()["id"]

        reviewer_id = self.create_user(
            email="reviewer@example.com",
            password="review-password"
        )
        self.create_review(
            self.login("reviewer@example.com", "review-password"),
            place_id
        )

        owner = facade.get_user(owner_id)
        reviewer = facade.get_user(reviewer_id)
        place = facade.get_place(place_id)
        amenity = facade.get_amenity(amenity_id)

        self.assertEqual(owner.places[0].id, place_id)
        self.assertEqual(reviewer.reviews[0].place.id, place_id)
        self.assertEqual(place.amenities[0].id, amenity_id)
        self.assertEqual(amenity.places[0].id, place_id)

    def test_model_validation_is_preserved(self):
        """Database mapping keeps Part 2 business validation."""
        self.create_user()
        headers = self.login()
        invalid_values = (
            ("price", -1),
            ("latitude", 91),
            ("longitude", 181)
        )

        for field, value in invalid_values:
            with self.subTest(field=field):
                data = {
                    "title": "Invalid Place",
                    "description": "Validation test",
                    "price": 50,
                    "latitude": 24.7,
                    "longitude": 46.7,
                    "amenities": []
                }
                data[field] = value
                response = self.client.post(
                    "/api/v1/places/",
                    json=data,
                    headers=headers
                )
                self.assertEqual(response.status_code, 400)

    def test_swagger_documents_part3_routes(self):
        """Swagger includes authentication and entity endpoints."""
        response = self.client.get("/swagger.json")
        self.assertEqual(response.status_code, 200)
        paths = response.get_json()["paths"]

        for path in (
            "/api/v1/auth/login",
            "/api/v1/protected",
            "/api/v1/users/",
            "/api/v1/amenities/",
            "/api/v1/places/",
            "/api/v1/reviews/"
        ):
            with self.subTest(path=path):
                self.assertIn(path, paths)


if __name__ == "__main__":
    unittest.main()
