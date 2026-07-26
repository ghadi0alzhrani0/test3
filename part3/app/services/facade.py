#!/usr/bin/python3
"""Define the facade used to connect application layers."""

from app.models.amenity import Amenity
from app.models.place import Place
from app.models.review import Review
from app.models.user import User
from app.persistence.repository import SQLAlchemyRepository
from app.services.repositories.user_repository import UserRepository


class HBnBFacade:
    """Provide a single interface to the business logic layer."""

    def __init__(self):
        """Initialize repositories for the main HBnB entities."""
        self.user_repo = UserRepository()
        self.place_repo = SQLAlchemyRepository(Place)
        self.review_repo = SQLAlchemyRepository(Review)
        self.amenity_repo = SQLAlchemyRepository(Amenity)

    def reset(self):
        """Reinitialize the entity repositories."""
        self.__init__()

    def create_user(self, user_data):
        """Create and store a new user."""
        if self.get_user_by_email(user_data.get("email")):
            raise ValueError("Email already registered")

        user = User(**user_data)
        self.user_repo.add(user)
        return user

    def get_user(self, user_id):
        """Retrieve a user by ID."""
        return self.user_repo.get(user_id)

    def get_user_by_email(self, email):
        """Retrieve a user by email."""
        if not email:
            return None

        return self.user_repo.get_user_by_email(email.strip())

    def get_all_users(self):
        """Retrieve every user."""
        return self.user_repo.get_all()

    def update_user(self, user_id, user_data):
        """Update an existing user."""
        user = self.get_user(user_id)
        if not user:
            return None

        data = user_data.copy()
        email = data.get("email")
        if email:
            existing_user = self.get_user_by_email(email)
            if existing_user and existing_user.id != user_id:
                raise ValueError("Email already registered")

        password = data.pop("password", None)
        if password is not None:
            user.hash_password(password)

        return self.user_repo.update(user_id, data)

    def create_amenity(self, amenity_data):
        """Create and store a new amenity."""
        name = amenity_data.get("name")
        if name and self.amenity_repo.get_by_attribute("name", name.strip()):
            raise ValueError("Amenity already exists")

        amenity = Amenity(**amenity_data)
        self.amenity_repo.add(amenity)
        return amenity

    def get_amenity(self, amenity_id):
        """Retrieve an amenity by ID."""
        return self.amenity_repo.get(amenity_id)

    def get_all_amenities(self):
        """Retrieve every amenity."""
        return self.amenity_repo.get_all()

    def update_amenity(self, amenity_id, amenity_data):
        """Update an existing amenity."""
        amenity = self.get_amenity(amenity_id)
        if not amenity:
            return None

        name = amenity_data.get("name")
        if name:
            existing = self.amenity_repo.get_by_attribute(
                "name",
                name.strip()
            )
            if existing and existing.id != amenity_id:
                raise ValueError("Amenity already exists")

        return self.amenity_repo.update(amenity_id, amenity_data)

    def create_place(self, place_data):
        """Create and store a new place."""
        data = place_data.copy()
        owner = self.get_user(data.pop("owner_id", None))
        if not owner:
            raise ValueError("Owner not found")

        amenities = self._get_amenities(data.pop("amenities", []))
        data.setdefault("description", "")
        place = Place(owner=owner, **data)
        place.set_amenities(amenities)
        self.place_repo.add(place)
        return place

    def get_place(self, place_id):
        """Retrieve a place by ID."""
        return self.place_repo.get(place_id)

    def get_all_places(self):
        """Retrieve every place."""
        return self.place_repo.get_all()

    def update_place(self, place_id, place_data):
        """Update an existing place."""
        place = self.get_place(place_id)
        if not place:
            return None

        data = place_data.copy()

        if "owner_id" in data:
            owner = self.get_user(data.pop("owner_id"))
            if not owner:
                raise ValueError("Owner not found")
            data["owner"] = owner

        if "amenities" in data:
            amenities = self._get_amenities(data.pop("amenities"))
            place.set_amenities(amenities)

        return self.place_repo.update(place_id, data)

    def delete_place(self, place_id):
        """Delete an existing place."""
        return self.place_repo.delete(place_id) is not None

    def create_review(self, review_data):
        """Create and store a new review."""
        data = review_data.copy()
        user = self.get_user(data.pop("user_id", None))
        place = self.get_place(data.pop("place_id", None))

        if not user:
            raise ValueError("User not found")
        if not place:
            raise ValueError("Place not found")
        if self.get_review_by_user_and_place(user.id, place.id):
            raise ValueError("You have already reviewed this place")

        review = Review(user=user, place=place, **data)
        self.review_repo.add(review)
        return review

    def get_review(self, review_id):
        """Retrieve a review by ID."""
        return self.review_repo.get(review_id)

    def get_all_reviews(self):
        """Retrieve every review."""
        return self.review_repo.get_all()

    def get_reviews_by_place(self, place_id):
        """Retrieve reviews for a specific place."""
        place = self.get_place(place_id)
        if not place:
            return None
        return place.reviews

    def get_review_by_user_and_place(self, user_id, place_id):
        """Retrieve a user's review for a place, if it exists."""
        return self.review_repo.get_by_attributes(
            user_id=user_id,
            place_id=place_id
        )

    def update_review(self, review_id, review_data):
        """Update an existing review."""
        review = self.get_review(review_id)
        if not review:
            return None

        data = review_data.copy()

        if "user_id" in data:
            user = self.get_user(data.pop("user_id"))
            if not user:
                raise ValueError("User not found")
            data["user"] = user

        if "place_id" in data:
            place = self.get_place(data.pop("place_id"))
            if not place:
                raise ValueError("Place not found")

            if place.id != review.place.id:
                review.place.remove_review(review)
                place.add_review(review)
            data["place"] = place

        return self.review_repo.update(review_id, data)

    def delete_review(self, review_id):
        """Delete an existing review."""
        review = self.get_review(review_id)
        if not review:
            return False

        return self.review_repo.delete(review_id) is not None

    def _get_amenities(self, amenity_ids):
        """Return amenity objects from a list of amenity IDs."""
        if amenity_ids is None:
            return []
        if not isinstance(amenity_ids, list):
            raise ValueError("Amenities must be a list")

        amenities = []
        for amenity_id in amenity_ids:
            amenity = self.get_amenity(amenity_id)
            if not amenity:
                raise ValueError("Amenity not found")
            amenities.append(amenity)

        return amenities
