#!/usr/bin/python3
"""Define the facade used to connect application layers."""

from app.models.amenity import Amenity, AmenityCategory
from app.models.booking import Booking, BookingGuest
from app.models.location import City, Country, State, _required_text
from app.models.notification import SystemNotification
from app.models.owner import Owner
from app.models.place import Place
from app.models.place_details import (
    CancellationPolicy,
    PlaceAvailability,
    PlaceType,
    RoomDetail,
    SeasonalPricing,
    _as_date,
    _required
)
from app.models.review import Review
from app.models.review_details import (
    GuestReview,
    ReviewRatingDetails,
    ReviewResponse,
    _rating
)
from app.models.user import User
from app.persistence.repository import InMemoryRepository


class HBnBFacade:
    """Provide a single interface to the business logic layer."""

    EXTENDED_REPOSITORIES = {
        "owners": "owner_repo",
        "countries": "country_repo",
        "states": "state_repo",
        "cities": "city_repo",
        "place_types": "place_type_repo",
        "cancellation_policies": "cancellation_policy_repo",
        "amenity_categories": "amenity_category_repo",
        "room_details": "room_detail_repo",
        "availability": "availability_repo",
        "seasonal_pricing": "seasonal_pricing_repo",
        "bookings": "booking_repo",
        "booking_guests": "booking_guest_repo",
        "booking_history": "booking_history_repo",
        "rating_details": "rating_details_repo",
        "review_responses": "review_response_repo",
        "guest_reviews": "guest_review_repo",
        "notifications": "notification_repo"
    }

    EXTENDED_UPDATE_FIELDS = {
        "owners": {
            "business_name", "contact_person", "email", "password",
            "phone_number", "commercial_register"
        },
        "countries": {"name", "code"},
        "states": {"name"},
        "cities": {"name"},
        "place_types": {"name"},
        "cancellation_policies": {"name", "description"},
        "amenity_categories": {"name"},
        "room_details": {"room_name", "bed_type", "beds_count"},
        "availability": {"start_date", "end_date", "is_booked"},
        "seasonal_pricing": {
            "start_date", "end_date", "special_price"
        },
        "booking_guests": {
            "adults_count", "children_count", "infants_count"
        },
        "rating_details": {
            "cleanliness", "accuracy", "communication", "location",
            "check_in", "value"
        },
        "review_responses": {"response_text"},
        "guest_reviews": {
            "cleanliness_rating", "communication_rating",
            "respect_rules_rating", "review_text"
        },
        "notifications": {"notification_type", "content", "is_seen"}
    }

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
        register = owner_data.get("commercial_register")
        if register and self.owner_repo.get_by_attribute(
            "commercial_register", register.strip()
        ):
            raise ValueError("Commercial register already registered")
        return self._store(self.owner_repo, Owner(**owner_data))

    def create_country(self, country_data):
        """Create a country."""
        name = country_data.get("name")
        code = country_data.get("code")
        if name and self.country_repo.get_by_attribute("name", name.strip()):
            raise ValueError("Country already exists")
        if code and self.country_repo.get_by_attribute(
            "code", code.strip().upper()
        ):
            raise ValueError("Country code already exists")
        return self._store(self.country_repo, Country(**country_data))

    def create_state(self, state_data):
        """Create a state linked to a country."""
        data = state_data.copy()
        country = self._required_object(
            self.country_repo,
            data.pop("country_id", None),
            "Country"
        )
        name = data.get("name")
        if self._related_name_exists(
            self.state_repo, name, "country", country
        ):
            raise ValueError("State already exists in this country")
        return self._store(self.state_repo, State(country=country, **data))

    def create_city(self, city_data):
        """Create a city linked to a state."""
        data = city_data.copy()
        state = self._required_object(
            self.state_repo,
            data.pop("state_id", None),
            "State"
        )
        name = data.get("name")
        if self._related_name_exists(self.city_repo, name, "state", state):
            raise ValueError("City already exists in this state")
        return self._store(self.city_repo, City(state=state, **data))

    def create_place_type(self, place_type_data):
        """Create a place type."""
        name = place_type_data.get("name")
        if name and self.place_type_repo.get_by_attribute(
            "name", name.strip()
        ):
            raise ValueError("Place type already exists")
        place_type = PlaceType(**place_type_data)
        return self._store(self.place_type_repo, place_type)

    def create_cancellation_policy(self, policy_data):
        """Create a cancellation policy."""
        name = policy_data.get("name")
        if name and self.cancellation_policy_repo.get_by_attribute(
            "name", name.strip()
        ):
            raise ValueError("Cancellation policy already exists")
        policy = CancellationPolicy(**policy_data)
        return self._store(self.cancellation_policy_repo, policy)

    def create_amenity_category(self, category_data):
        """Create an amenity category."""
        name = category_data.get("name")
        if name and self.amenity_category_repo.get_by_attribute(
            "name", name.strip()
        ):
            raise ValueError("Amenity category already exists")
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
        if booking.guest_details is not None:
            raise ValueError("Booking guest details already exist")
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
        if review.rating_details is not None:
            raise ValueError("Review rating details already exist")
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
        if review.response is not None:
            raise ValueError("Review response already exists")
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
        if booking.guest_review is not None:
            raise ValueError("Guest review already exists for this booking")
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

    def get_extended_resource(self, resource, object_id):
        """Retrieve one extended entity through its repository."""
        return self._extended_repository(resource).get(object_id)

    def get_all_extended_resources(self, resource):
        """Retrieve all objects for an extended entity."""
        return self._extended_repository(resource).get_all()

    def update_extended_resource(self, resource, object_id, data):
        """Validate and update fields supported by an extended entity."""
        repository = self._extended_repository(resource)
        obj = repository.get(object_id)
        if obj is None:
            return None

        allowed = self.EXTENDED_UPDATE_FIELDS.get(resource)
        if allowed is None:
            raise ValueError("This resource is read-only")
        unknown = set(data) - allowed
        if unknown:
            raise ValueError(f"Unsupported field: {sorted(unknown)[0]}")

        prepared = self._prepare_extended_update(resource, obj, data)
        obj.update(prepared)
        return obj

    def mark_notification_read(self, notification_id):
        """Mark a stored notification as read."""
        notification = self.notification_repo.get(notification_id)
        if notification is None:
            return None
        notification.mark_as_read()
        return notification

    def _extended_repository(self, resource):
        """Return the repository assigned to an extended resource name."""
        repository_name = self.EXTENDED_REPOSITORIES.get(resource)
        if repository_name is None:
            raise ValueError("Unsupported resource")
        return getattr(self, repository_name)

    @staticmethod
    def _related_name_exists(
        repository, name, field, related, current_id=None
    ):
        """Return whether a related collection already uses a name."""
        if not isinstance(name, str):
            return False
        normalized = name.strip().lower()
        return any(
            item.id != current_id
            and item.name.lower() == normalized
            and getattr(item, field) is related
            for item in repository.get_all()
        )

    @staticmethod
    def _attribute_exists(repository, field, value, current_id=None):
        """Return whether another object already uses an attribute value."""
        if isinstance(value, str):
            value = value.strip().lower()
        return any(
            item.id != current_id
            and (
                getattr(item, field).lower()
                if isinstance(getattr(item, field), str)
                else getattr(item, field)
            ) == value
            for item in repository.get_all()
        )

    def _prepare_extended_update(self, resource, obj, data):
        """Normalize values before updating an extended entity."""
        prepared = data.copy()

        if resource == "owners":
            labels = {
                "business_name": ("Business name", 255),
                "contact_person": ("Contact person", 100),
                "password": ("Password", 128),
                "phone_number": ("Phone number", 30),
                "commercial_register": ("Commercial register", 50)
            }
            for field, (label, maximum) in labels.items():
                if field in prepared:
                    prepared[field] = Owner._required(
                        prepared[field], label, maximum
                    )
            if "email" in prepared:
                email = Owner._validate_email(prepared["email"])
                existing = self.owner_repo.get_by_attribute("email", email)
                if existing and existing.id != obj.id:
                    raise ValueError("Owner email already registered")
                prepared["email"] = email
            if "commercial_register" in prepared and self._attribute_exists(
                self.owner_repo,
                "commercial_register",
                prepared["commercial_register"],
                obj.id
            ):
                raise ValueError("Commercial register already registered")
        elif resource == "countries":
            if "name" in prepared:
                prepared["name"] = _required_text(
                    prepared["name"], "Country name"
                )
            if "code" in prepared:
                prepared["code"] = _required_text(
                    prepared["code"], "Country code", 3
                ).upper()
            for field, message in (
                ("name", "Country already exists"),
                ("code", "Country code already exists")
            ):
                if field in prepared and self._attribute_exists(
                    self.country_repo, field, prepared[field], obj.id
                ):
                    raise ValueError(message)
        elif resource in {"states", "cities"} and "name" in prepared:
            prepared["name"] = _required_text(prepared["name"], "Name")
            related_field = "country" if resource == "states" else "state"
            if self._related_name_exists(
                self._extended_repository(resource),
                prepared["name"],
                related_field,
                getattr(obj, related_field),
                obj.id
            ):
                raise ValueError(f"{resource[:-1].title()} already exists")
        elif resource == "place_types" and "name" in prepared:
            prepared["name"] = _required(prepared["name"], "Place type name")
            if self._attribute_exists(
                self.place_type_repo, "name", prepared["name"], obj.id
            ):
                raise ValueError("Place type already exists")
        elif resource == "cancellation_policies":
            if "name" in prepared:
                prepared["name"] = _required(prepared["name"], "Policy name")
            if "description" in prepared:
                prepared["description"] = _required(
                    prepared["description"], "Policy description", 1000
                )
            if "name" in prepared and self._attribute_exists(
                self.cancellation_policy_repo,
                "name",
                prepared["name"],
                obj.id
            ):
                raise ValueError("Cancellation policy already exists")
        elif resource == "amenity_categories" and "name" in prepared:
            prepared["name"] = AmenityCategory._validate_name(
                prepared["name"], "Amenity category name", 100
            )
            if self._attribute_exists(
                self.amenity_category_repo, "name", prepared["name"], obj.id
            ):
                raise ValueError("Amenity category already exists")
        elif resource == "room_details":
            for field in ("room_name", "bed_type"):
                if field in prepared:
                    prepared[field] = _required(
                        prepared[field], field.replace("_", " ").title()
                    )
            if "beds_count" in prepared and (
                not isinstance(prepared["beds_count"], int)
                or prepared["beds_count"] < 1
            ):
                raise ValueError("Beds count must be a positive integer")
        elif resource in {"availability", "seasonal_pricing"}:
            for field in ("start_date", "end_date"):
                if field in prepared:
                    prepared[field] = _as_date(
                        prepared[field], field.replace("_", " ").title()
                    )
            start_date = prepared.get("start_date", obj.start_date)
            end_date = prepared.get("end_date", obj.end_date)
            if end_date <= start_date:
                raise ValueError("End date must be after start date")
            if "is_booked" in prepared and not isinstance(
                prepared["is_booked"], bool
            ):
                raise ValueError("is_booked must be a boolean")
            if "special_price" in prepared:
                prepared["special_price"] = float(prepared["special_price"])
                if prepared["special_price"] < 0:
                    raise ValueError("Special price must be non-negative")
        elif resource == "booking_guests":
            counts = {
                "adults_count": prepared.get(
                    "adults_count", obj.adults_count
                ),
                "children_count": prepared.get(
                    "children_count", obj.children_count
                ),
                "infants_count": prepared.get(
                    "infants_count", obj.infants_count
                )
            }
            if any(
                not isinstance(value, int) or value < 0
                for value in counts.values()
            ):
                raise ValueError("Guest counts must be non-negative integers")
            if counts["adults_count"] < 1:
                raise ValueError("At least one adult is required")
        elif resource in {"rating_details", "guest_reviews"}:
            for field, value in prepared.items():
                if field.endswith("rating") or field in {
                    "cleanliness", "accuracy", "communication", "location",
                    "check_in", "value"
                }:
                    prepared[field] = _rating(
                        value, field.replace("_", " ").title()
                    )
            if "review_text" in prepared:
                prepared["review_text"] = _required(
                    prepared["review_text"], "Review text", 1000
                )
        elif resource == "review_responses" and "response_text" in prepared:
            prepared["response_text"] = _required(
                prepared["response_text"], "Response text", 1000
            )
        elif resource == "notifications":
            for field in ("notification_type", "content"):
                if field in prepared:
                    prepared[field] = _required(
                        prepared[field], field.replace("_", " ").title(), 1000
                    )
            if "is_seen" in prepared and not isinstance(
                prepared["is_seen"], bool
            ):
                raise ValueError("is_seen must be a boolean")

        return prepared

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
