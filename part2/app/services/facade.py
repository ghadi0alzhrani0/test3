#!/usr/bin/python3
"""Define the facade used to connect application layers."""

from app.models.amenity import Amenity, AmenityCategory
from app.models.booking import Booking, BookingGuest
from app.models.location import City, Country, State
from app.models.notification import SystemNotification
from app.models.owner import Owner
from app.models.place import Place
from app.models.place_details import (
    CancellationPolicy,
    PlaceAvailability,
    PlaceType,
    RoomDetail,
    SeasonalPricing
)
from app.models.review import Review
from app.models.review_details import (
    GuestReview,
    ReviewRatingDetails,
    ReviewResponse
)
from app.models.user import User
from app.persistence.repository import InMemoryRepository


class HBnBFacade:
    """Provide a single interface to the business logic layer."""

    def __init__(self):
        """Initialize repositories for the main HBnB entities."""
        self.user_repo = InMemoryRepository()
        self.place_repo = InMemoryRepository()
        self.review_repo = InMemoryRepository()
        self.amenity_repo = InMemoryRepository()
        self.owner_repo = InMemoryRepository()
        self.country_repo = InMemoryRepository()
        self.state_repo = InMemoryRepository()
        self.city_repo = InMemoryRepository()
        self.place_type_repo = InMemoryRepository()
        self.cancellation_policy_repo = InMemoryRepository()
        self.room_detail_repo = InMemoryRepository()
        self.availability_repo = InMemoryRepository()
        self.seasonal_pricing_repo = InMemoryRepository()
        self.amenity_category_repo = InMemoryRepository()
        self.booking_repo = InMemoryRepository()
        self.booking_guest_repo = InMemoryRepository()
        self.booking_history_repo = InMemoryRepository()
        self.rating_details_repo = InMemoryRepository()
        self.review_response_repo = InMemoryRepository()
        self.guest_review_repo = InMemoryRepository()
        self.notification_repo = InMemoryRepository()

    def reset(self):
        """Reset in-memory repositories."""
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

        email = email.strip().lower()
        return next(
            (
                user
                for user in self.user_repo.get_all()
                if user.email.lower() == email
            ),
            None
        )

    def get_all_users(self):
        """Retrieve every user."""
        return self.user_repo.get_all()

    def update_user(self, user_id, user_data):
        """Update an existing user."""
        user = self.get_user(user_id)
        if not user:
            return None

        email = user_data.get("email")
        existing_user = self.get_user_by_email(email)
        if existing_user and existing_user.id != user_id:
            raise ValueError("Email already registered")

        user.update(user_data)
        return user

    def create_amenity(self, amenity_data):
        """Create and store a new amenity."""
        data = amenity_data.copy()
        category_id = data.pop("category_id", None)
        category = None
        if category_id is not None:
            category = self._required_object(
                self.amenity_category_repo,
                category_id,
                "Amenity category"
            )
        amenity = Amenity(category=category, **data)
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

        data = amenity_data.copy()
        if "category_id" in data:
            category_id = data.pop("category_id")
            data["category"] = (
                self._required_object(
                    self.amenity_category_repo,
                    category_id,
                    "Amenity category"
                )
                if category_id is not None else None
            )
        amenity.update(data)
        return amenity

    def create_place(self, place_data):
        """Create and store a new place."""
        data = place_data.copy()
        owner = self.get_user(data.pop("owner_id", None))
        if not owner:
            raise ValueError("Owner not found")

        amenities = self._get_amenities(data.pop("amenities", []))
        relationships = {
            "city": (self.city_repo, data.pop("city_id", None), "City"),
            "place_type": (
                self.place_type_repo,
                data.pop("place_type_id", None),
                "Place type"
            ),
            "cancellation_policy": (
                self.cancellation_policy_repo,
                data.pop("cancellation_policy_id", None),
                "Cancellation policy"
            ),
            "business_owner": (
                self.owner_repo,
                data.pop("business_owner_id", None),
                "Business owner"
            )
        }
        for field, (repository, object_id, label) in relationships.items():
            if object_id is not None:
                data[field] = self._required_object(
                    repository,
                    object_id,
                    label
                )
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

        relationships = {
            "city_id": ("city", self.city_repo, "City"),
            "place_type_id": (
                "place_type",
                self.place_type_repo,
                "Place type"
            ),
            "cancellation_policy_id": (
                "cancellation_policy",
                self.cancellation_policy_repo,
                "Cancellation policy"
            ),
            "business_owner_id": (
                "business_owner",
                self.owner_repo,
                "Business owner"
            )
        }
        for id_field, (field, repository, label) in relationships.items():
            if id_field in data:
                object_id = data.pop(id_field)
                data[field] = (
                    self._required_object(repository, object_id, label)
                    if object_id is not None else None
                )

        place.update(data)
        return place

    def create_review(self, review_data):
        """Create and store a new review."""
        data = review_data.copy()
        user = self.get_user(data.pop("user_id", None))
        place = self.get_place(data.pop("place_id", None))

        if not user:
            raise ValueError("User not found")
        if not place:
            raise ValueError("Place not found")

        review = Review(user=user, place=place, **data)
        self.review_repo.add(review)
        place.add_review(review)
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

        review.update(data)
        return review

    def delete_review(self, review_id):
        """Delete an existing review."""
        review = self.get_review(review_id)
        if not review:
            return False

        review.place.remove_review(review)
        self.review_repo.delete(review_id)
        return True

    def create_owner(self, owner_data):
        """Create a business owner from the extended Part 1 design."""
        email = owner_data.get("email")
        if email and self.owner_repo.get_by_attribute(
            "email",
            email.strip().lower()
        ):
            raise ValueError("Owner email already registered")
        return self._store(self.owner_repo, Owner(**owner_data))

    def create_country(self, country_data):
        """Create a country."""
        return self._store(self.country_repo, Country(**country_data))

    def create_state(self, state_data):
        """Create a state linked to a country."""
        data = state_data.copy()
        country = self._required_object(
            self.country_repo,
            data.pop("country_id", None),
            "Country"
        )
        return self._store(self.state_repo, State(country=country, **data))

    def create_city(self, city_data):
        """Create a city linked to a state."""
        data = city_data.copy()
        state = self._required_object(
            self.state_repo,
            data.pop("state_id", None),
            "State"
        )
        return self._store(self.city_repo, City(state=state, **data))

    def create_place_type(self, place_type_data):
        """Create a place type."""
        place_type = PlaceType(**place_type_data)
        return self._store(self.place_type_repo, place_type)

    def create_cancellation_policy(self, policy_data):
        """Create a cancellation policy."""
        policy = CancellationPolicy(**policy_data)
        return self._store(self.cancellation_policy_repo, policy)

    def create_amenity_category(self, category_data):
        """Create an amenity category."""
        category = AmenityCategory(**category_data)
        return self._store(self.amenity_category_repo, category)

    def create_room_detail(self, room_data):
        """Add room details to a place."""
        data = room_data.copy()
        place = self._required_object(
            self.place_repo,
            data.pop("place_id", None),
            "Place"
        )
        return self._store(
            self.room_detail_repo,
            RoomDetail(place=place, **data)
        )

    def create_place_availability(self, availability_data):
        """Add an availability period to a place."""
        data = availability_data.copy()
        place = self._required_object(
            self.place_repo,
            data.pop("place_id", None),
            "Place"
        )
        period = PlaceAvailability(place=place, **data)
        return self._store(self.availability_repo, period)

    def create_seasonal_pricing(self, pricing_data):
        """Add seasonal pricing to a place."""
        data = pricing_data.copy()
        place = self._required_object(
            self.place_repo,
            data.pop("place_id", None),
            "Place"
        )
        pricing = SeasonalPricing(place=place, **data)
        return self._store(self.seasonal_pricing_repo, pricing)

    def create_booking(self, booking_data):
        """Create a booking linked to a user and place."""
        data = booking_data.copy()
        place = self._required_object(
            self.place_repo,
            data.pop("place_id", None),
            "Place"
        )
        user = self._required_object(
            self.user_repo,
            data.pop("user_id", None),
            "User"
        )
        if not place.check_availability(data["start_date"], data["end_date"]):
            raise ValueError("Place is not available for these dates")
        booking = Booking(place=place, user=user, **data)
        return self._store(self.booking_repo, booking)

    def create_booking_guest(self, guest_data):
        """Create guest counts for a booking."""
        data = guest_data.copy()
        booking = self._required_object(
            self.booking_repo,
            data.pop("booking_id", None),
            "Booking"
        )
        details = BookingGuest(booking=booking, **data)
        return self._store(self.booking_guest_repo, details)

    def update_booking_status(self, booking_id, status):
        """Apply a supported booking status transition."""
        booking = self._required_object(
            self.booking_repo,
            booking_id,
            "Booking"
        )
        transitions = {
            "confirmed": booking.confirm,
            "cancelled": booking.cancel,
            "checked_in": booking.check_in
        }
        if status not in transitions:
            raise ValueError("Unsupported booking status transition")
        transitions[status]()
        history = booking.history[-1]
        self._store(self.booking_history_repo, history)
        return booking

    def create_review_rating_details(self, rating_data):
        """Create category ratings for a place review."""
        data = rating_data.copy()
        review = self._required_object(
            self.review_repo,
            data.pop("review_id", None),
            "Review"
        )
        details = ReviewRatingDetails(review=review, **data)
        return self._store(self.rating_details_repo, details)

    def create_review_response(self, response_data):
        """Create a business owner's response to a place review."""
        data = response_data.copy()
        review = self._required_object(
            self.review_repo,
            data.pop("review_id", None),
            "Review"
        )
        owner = self._required_object(
            self.owner_repo,
            data.pop("owner_id", None),
            "Owner"
        )
        response = ReviewResponse(review=review, owner=owner, **data)
        return self._store(self.review_response_repo, response)

    def create_guest_review(self, guest_review_data):
        """Create a business owner's review of a booking guest."""
        data = guest_review_data.copy()
        booking = self._required_object(
            self.booking_repo,
            data.pop("booking_id", None),
            "Booking"
        )
        owner = self._required_object(
            self.owner_repo,
            data.pop("owner_id", None),
            "Owner"
        )
        guest = self._required_object(
            self.user_repo,
            data.pop("guest_id", None),
            "Guest"
        )
        review = GuestReview(
            booking=booking,
            owner=owner,
            guest=guest,
            **data
        )
        return self._store(self.guest_review_repo, review)

    def create_notification(self, notification_data):
        """Create a notification for a user, owner, or both."""
        data = notification_data.copy()
        user_id = data.pop("user_id", None)
        owner_id = data.pop("owner_id", None)
        user = self.user_repo.get(user_id) if user_id else None
        owner = self.owner_repo.get(owner_id) if owner_id else None
        if user_id and user is None:
            raise ValueError("User not found")
        if owner_id and owner is None:
            raise ValueError("Owner not found")
        notification = SystemNotification(
            user=user,
            owner=owner,
            **data
        )
        return self._store(self.notification_repo, notification)

    @staticmethod
    def _store(repository, obj):
        """Store and return an object."""
        repository.add(obj)
        return obj

    @staticmethod
    def _required_object(repository, object_id, label):
        """Return a related object or raise a clear validation error."""
        obj = repository.get(object_id) if object_id else None
        if obj is None:
            raise ValueError(f"{label} not found")
        return obj

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
