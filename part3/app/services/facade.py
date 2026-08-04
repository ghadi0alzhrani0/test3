#!/usr/bin/python3
"""Define the facade used to connect application layers."""

from app.models.amenity import Amenity, AmenityCategory
from app.models.booking import Booking, BookingGuest, BookingHistory
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
        self.owner_repo = SQLAlchemyRepository(Owner)
        self.country_repo = SQLAlchemyRepository(Country)
        self.state_repo = SQLAlchemyRepository(State)
        self.city_repo = SQLAlchemyRepository(City)
        self.place_type_repo = SQLAlchemyRepository(PlaceType)
        self.cancellation_policy_repo = SQLAlchemyRepository(
            CancellationPolicy
        )
        self.room_detail_repo = SQLAlchemyRepository(RoomDetail)
        self.availability_repo = SQLAlchemyRepository(PlaceAvailability)
        self.seasonal_pricing_repo = SQLAlchemyRepository(SeasonalPricing)
        self.amenity_category_repo = SQLAlchemyRepository(AmenityCategory)
        self.booking_repo = SQLAlchemyRepository(Booking)
        self.booking_guest_repo = SQLAlchemyRepository(BookingGuest)
        self.booking_history_repo = SQLAlchemyRepository(BookingHistory)
        self.rating_details_repo = SQLAlchemyRepository(ReviewRatingDetails)
        self.review_response_repo = SQLAlchemyRepository(ReviewResponse)
        self.guest_review_repo = SQLAlchemyRepository(GuestReview)
        self.notification_repo = SQLAlchemyRepository(SystemNotification)

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
        data = amenity_data.copy()
        name = data.get("name")
        if name and self.amenity_repo.get_by_attribute("name", name.strip()):
            raise ValueError("Amenity already exists")

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
        name = data.get("name")
        if name:
            existing = self.amenity_repo.get_by_attribute(
                "name",
                name.strip()
            )
            if existing and existing.id != amenity_id:
                raise ValueError("Amenity already exists")

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

        return self.amenity_repo.update(amenity_id, data)

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
        return self._store(
            self.place_type_repo,
            PlaceType(**place_type_data)
        )

    def create_cancellation_policy(self, policy_data):
        """Create a cancellation policy."""
        return self._store(
            self.cancellation_policy_repo,
            CancellationPolicy(**policy_data)
        )

    def create_amenity_category(self, category_data):
        """Create an amenity category."""
        return self._store(
            self.amenity_category_repo,
            AmenityCategory(**category_data)
        )

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
        history = transitions[status]()
        self.booking_history_repo.add(history)
        return history

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
