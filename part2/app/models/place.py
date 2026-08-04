#!/usr/bin/python3
"""Define the Place business entity."""

from datetime import date

from app.models.amenity import Amenity
from app.models.base_model import BaseModel
from app.models.location import City
from app.models.owner import Owner
from app.models.place_details import CancellationPolicy, PlaceType, _as_date
from app.models.user import User


class Place(BaseModel):
    """Represent a rentable place."""

    def __init__(
        self,
        title,
        description,
        price,
        latitude,
        longitude,
        owner,
        city=None,
        place_type=None,
        cancellation_policy=None,
        number_rooms=0,
        number_bathrooms=0,
        max_guest=1,
        business_owner=None
    ):
        """Initialize a place with validated attributes."""
        super().__init__()
        self.title = title
        self.description = description
        self.price = price
        self.latitude = latitude
        self.longitude = longitude
        self.owner = owner
        self.city = self._optional_model(city, City, "City")
        self.place_type = self._optional_model(
            place_type,
            PlaceType,
            "Place type"
        )
        self.cancellation_policy = self._optional_model(
            cancellation_policy,
            CancellationPolicy,
            "Cancellation policy"
        )
        self.business_owner = self._optional_model(
            business_owner,
            Owner,
            "Business owner"
        )
        self.number_rooms = self._count(number_rooms, "Number of rooms")
        self.number_bathrooms = self._count(
            number_bathrooms,
            "Number of bathrooms"
        )
        self.max_guest = self._count(max_guest, "Maximum guests", minimum=1)
        self.reviews = []
        self.amenities = []
        self.room_details = []
        self.availability_periods = []
        self.seasonal_pricing = []
        self.bookings = []
        owner.places.append(self)
        if city is not None:
            city.add_place(self)
        if place_type is not None:
            place_type.places.append(self)
        if cancellation_policy is not None:
            cancellation_policy.places.append(self)
        if business_owner is not None:
            business_owner.add_place(self)

    @staticmethod
    def _optional_model(value, model, field):
        """Validate an optional related model."""
        if value is not None and not isinstance(value, model):
            raise ValueError(f"{field} must be valid")
        return value

    @staticmethod
    def _count(value, field, minimum=0):
        """Validate an integer count."""
        if not isinstance(value, int) or isinstance(value, bool):
            raise ValueError(f"{field} must be an integer")
        if value < minimum:
            raise ValueError(f"{field} must be at least {minimum}")
        return value

    @property
    def name(self):
        """Return the Part 1 name alias for the place title."""
        return self.title

    @name.setter
    def name(self, value):
        """Update the place title through its Part 1 alias."""
        self.title = value

    @property
    def price_by_night(self):
        """Return the Part 1 alias for the nightly price."""
        return self.price

    @price_by_night.setter
    def price_by_night(self, value):
        """Update the nightly price through its Part 1 alias."""
        self.price = value

    @property
    def title(self):
        """Return the place title."""
        return self._title

    @title.setter
    def title(self, value):
        """Validate and set the place title."""
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Title is required")
        if len(value.strip()) > 100:
            raise ValueError("Title must be 100 characters or fewer")
        self._title = value.strip()

    @property
    def description(self):
        """Return the place description."""
        return self._description

    @description.setter
    def description(self, value):
        """Validate and set the place description."""
        if value is None:
            value = ""
        if not isinstance(value, str):
            raise ValueError("Description must be a string")
        self._description = value

    @property
    def price(self):
        """Return the nightly price."""
        return self._price

    @price.setter
    def price(self, value):
        """Validate and set the nightly price."""
        try:
            price = float(value)
        except (TypeError, ValueError) as exc:
            raise ValueError("Price must be a number") from exc

        if price < 0:
            raise ValueError("Price must be non-negative")
        self._price = price

    @property
    def latitude(self):
        """Return the latitude."""
        return self._latitude

    @latitude.setter
    def latitude(self, value):
        """Validate and set the latitude."""
        try:
            latitude = float(value)
        except (TypeError, ValueError) as exc:
            raise ValueError("Latitude must be a number") from exc

        if latitude < -90 or latitude > 90:
            raise ValueError("Latitude must be between -90 and 90")
        self._latitude = latitude

    @property
    def longitude(self):
        """Return the longitude."""
        return self._longitude

    @longitude.setter
    def longitude(self, value):
        """Validate and set the longitude."""
        try:
            longitude = float(value)
        except (TypeError, ValueError) as exc:
            raise ValueError("Longitude must be a number") from exc

        if longitude < -180 or longitude > 180:
            raise ValueError("Longitude must be between -180 and 180")
        self._longitude = longitude

    @property
    def owner(self):
        """Return the owner."""
        return self._owner

    @owner.setter
    def owner(self, value):
        """Validate and set the owner."""
        if not isinstance(value, User):
            raise ValueError("Owner must be a valid user")
        self._owner = value

    def add_review(self, review):
        """Attach a review to the place."""
        from app.models.review import Review

        if not isinstance(review, Review):
            raise ValueError("Review must be valid")
        if review not in self.reviews:
            self.reviews.append(review)
            self.save()

    def remove_review(self, review):
        """Detach a review from the place."""
        if review in self.reviews:
            self.reviews.remove(review)
            self.save()

    def add_amenity(self, amenity):
        """Attach an amenity to the place."""
        if not isinstance(amenity, Amenity):
            raise ValueError("Amenity must be valid")
        if amenity not in self.amenities:
            self.amenities.append(amenity)
            self.save()

    def set_amenities(self, amenities):
        """Replace the place amenities."""
        if amenities is None:
            amenities = []
        if not isinstance(amenities, list):
            raise ValueError("Amenities must be a list")
        if any(not isinstance(amenity, Amenity) for amenity in amenities):
            raise ValueError("Amenities must be valid")

        self.amenities = []
        for amenity in amenities:
            self.add_amenity(amenity)
        self.save()

    def add_room_detail(self, room_detail):
        """Attach room details to the place."""
        if room_detail not in self.room_details:
            self.room_details.append(room_detail)
            self.save()

    def add_availability(self, availability):
        """Attach an availability period to the place."""
        if availability not in self.availability_periods:
            self.availability_periods.append(availability)
            self.save()

    def add_seasonal_pricing(self, pricing):
        """Attach a special pricing period to the place."""
        if pricing not in self.seasonal_pricing:
            self.seasonal_pricing.append(pricing)
            self.save()

    def check_availability(self, start_date, end_date):
        """Return whether a place is free for the requested range."""
        start_date = _as_date(start_date, "Start date")
        end_date = _as_date(end_date, "End date")
        if end_date <= start_date:
            raise ValueError("End date must be after start date")
        for period in self.availability_periods:
            overlaps = (
                start_date < period.end_date
                and end_date > period.start_date
            )
            if overlaps and period.is_booked:
                return False
        for booking in self.bookings:
            overlaps = (
                start_date < booking.end_date
                and end_date > booking.start_date
            )
            if overlaps and booking.status not in {"cancelled", "completed"}:
                return False
        return True

    def calculate_total_price(self, start_date, end_date):
        """Calculate the nightly total, including seasonal prices."""
        start_date = _as_date(start_date, "Start date")
        end_date = _as_date(end_date, "End date")
        if end_date <= start_date:
            raise ValueError("End date must be after start date")
        total = 0.0
        current = start_date
        while current < end_date:
            price = self.price
            for seasonal in self.seasonal_pricing:
                if seasonal.is_active(current):
                    price = seasonal.special_price
                    break
            total += price
            current = date.fromordinal(current.toordinal() + 1)
        return total

    def get_average_ratings(self):
        """Return the average rating from all place reviews."""
        if not self.reviews:
            return 0.0
        total = sum(review.rating for review in self.reviews)
        return total / len(self.reviews)
