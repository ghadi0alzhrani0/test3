#!/usr/bin/python3
"""Initialize the HBnB Flask application."""

from flask import Flask
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_restx import Api
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
jwt = JWTManager()
db = SQLAlchemy()


def create_app(config_class="config.DevelopmentConfig"):
    """Create and configure the Flask application."""
    from app.api.v1.amenities import api as amenities_ns
    from app.api.v1.amenity_categories import api as amenity_categories_ns
    from app.api.v1.auth import api as auth_ns
    from app.api.v1.bookings import (
        bookings_api,
        guests_api as booking_guests_ns,
        history_api as booking_history_ns
    )
    from app.api.v1.locations import cities_api, countries_api, states_api
    from app.api.v1.notifications import api as notifications_ns
    from app.api.v1.owners import api as owners_ns
    from app.api.v1.places import api as places_ns
    from app.api.v1.place_details import (
        availability_api,
        place_types_api,
        policies_api,
        pricing_api,
        rooms_api
    )
    from app.api.v1.protected import api as protected_ns
    from app.api.v1.reviews import api as reviews_ns
    from app.api.v1.review_details import (
        guest_reviews_api,
        ratings_api,
        responses_api
    )
    from app.api.v1.users import api as users_ns

    app = Flask(__name__)
    app.config.from_object(config_class)
    bcrypt.init_app(app)
    jwt.init_app(app)
    db.init_app(app)

    api = Api(
        app,
        version="1.0",
        title="HBnB API",
        description="HBnB Application API",
        doc="/api/v1/"
    )

    api.add_namespace(auth_ns, path="/api/v1/auth")
    api.add_namespace(protected_ns, path="/api/v1/protected")
    api.add_namespace(users_ns, path="/api/v1/users")
    api.add_namespace(amenities_ns, path="/api/v1/amenities")
    api.add_namespace(places_ns, path="/api/v1/places")
    api.add_namespace(reviews_ns, path="/api/v1/reviews")
    api.add_namespace(owners_ns, path="/api/v1/owners")
    api.add_namespace(countries_api, path="/api/v1/countries")
    api.add_namespace(states_api, path="/api/v1/states")
    api.add_namespace(cities_api, path="/api/v1/cities")
    api.add_namespace(place_types_api, path="/api/v1/place-types")
    api.add_namespace(policies_api, path="/api/v1/cancellation-policies")
    api.add_namespace(
        amenity_categories_ns,
        path="/api/v1/amenity-categories"
    )
    api.add_namespace(rooms_api, path="/api/v1/room-details")
    api.add_namespace(availability_api, path="/api/v1/place-availability")
    api.add_namespace(pricing_api, path="/api/v1/seasonal-pricing")
    api.add_namespace(bookings_api, path="/api/v1/bookings")
    api.add_namespace(booking_guests_ns, path="/api/v1/booking-guests")
    api.add_namespace(booking_history_ns, path="/api/v1/booking-history")
    api.add_namespace(ratings_api, path="/api/v1/review-ratings")
    api.add_namespace(responses_api, path="/api/v1/review-responses")
    api.add_namespace(guest_reviews_api, path="/api/v1/guest-reviews")
    api.add_namespace(notifications_ns, path="/api/v1/notifications")

    return app
