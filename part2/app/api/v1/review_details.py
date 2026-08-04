#!/usr/bin/python3
"""Define endpoints for detailed ratings and business review records."""

from flask_restx import Namespace, Resource, fields

from app.api.v1.extended_helpers import (
    serialize_guest_review,
    serialize_rating_details,
    serialize_review_response
)
from app.services import facade


ratings_api = Namespace(
    "review-ratings",
    description="Detailed rating operations"
)
responses_api = Namespace(
    "review-responses",
    description="Business review response operations"
)
guest_reviews_api = Namespace(
    "guest-reviews",
    description="Guest review operations"
)

rating_fields = {
    "cleanliness": fields.Integer(required=True, min=1, max=5),
    "accuracy": fields.Integer(required=True, min=1, max=5),
    "communication": fields.Integer(required=True, min=1, max=5),
    "location": fields.Integer(required=True, min=1, max=5),
    "check_in": fields.Integer(required=True, min=1, max=5),
    "value": fields.Integer(required=True, min=1, max=5)
}
rating_model = ratings_api.model(
    "ReviewRatingDetails",
    {"review_id": fields.String(required=True), **rating_fields}
)
rating_update_model = ratings_api.model(
    "ReviewRatingDetailsUpdate",
    {
        name: fields.Integer(min=1, max=5)
        for name in rating_fields
    }
)
response_model = responses_api.model("ReviewResponse", {
    "review_id": fields.String(required=True),
    "owner_id": fields.String(required=True),
    "response_text": fields.String(required=True)
})
response_update_model = responses_api.model("ReviewResponseUpdate", {
    "response_text": fields.String()
})
guest_review_model = guest_reviews_api.model("GuestReview", {
    "booking_id": fields.String(required=True),
    "owner_id": fields.String(required=True),
    "guest_id": fields.String(required=True),
    "cleanliness_rating": fields.Integer(required=True, min=1, max=5),
    "communication_rating": fields.Integer(required=True, min=1, max=5),
    "respect_rules_rating": fields.Integer(required=True, min=1, max=5),
    "review_text": fields.String(required=True)
})
guest_review_update_model = guest_reviews_api.model("GuestReviewUpdate", {
    "cleanliness_rating": fields.Integer(min=1, max=5),
    "communication_rating": fields.Integer(min=1, max=5),
    "respect_rules_rating": fields.Integer(min=1, max=5),
    "review_text": fields.String()
})


def _get(resource, object_id, label, serializer):
    """Return one detailed review object."""
    obj = facade.get_extended_resource(resource, object_id)
    if obj is None:
        return {"error": f"{label} not found"}, 404
    return serializer(obj), 200


def _update(resource, object_id, payload, label, serializer):
    """Update one detailed review object."""
    try:
        obj = facade.update_extended_resource(resource, object_id, payload)
    except ValueError as exc:
        return {"error": str(exc)}, 400
    if obj is None:
        return {"error": f"{label} not found"}, 404
    return serializer(obj), 200


@ratings_api.route("/")
class RatingList(Resource):
    """Handle detailed place review ratings."""

    @ratings_api.expect(rating_model, validate=True)
    def post(self):
        """Create detailed category ratings."""
        try:
            obj = facade.create_review_rating_details(
                ratings_api.payload or {}
            )
        except ValueError as exc:
            return {"error": str(exc)}, 400
        return serialize_rating_details(obj), 201

    def get(self):
        """Retrieve all detailed ratings."""
        objects = facade.get_all_extended_resources("rating_details")
        return [serialize_rating_details(obj) for obj in objects], 200


@ratings_api.route("/<object_id>")
class RatingResource(Resource):
    """Handle one detailed rating record."""

    def get(self, object_id):
        """Retrieve detailed ratings."""
        return _get(
            "rating_details", object_id, "Rating details",
            serialize_rating_details
        )

    @ratings_api.expect(rating_update_model, validate=True)
    def put(self, object_id):
        """Update detailed ratings."""
        return _update(
            "rating_details", object_id, ratings_api.payload or {},
            "Rating details", serialize_rating_details
        )


@responses_api.route("/")
class ResponseList(Resource):
    """Handle owner responses to place reviews."""

    @responses_api.expect(response_model, validate=True)
    def post(self):
        """Create an owner response."""
        try:
            obj = facade.create_review_response(responses_api.payload or {})
        except ValueError as exc:
            return {"error": str(exc)}, 400
        return serialize_review_response(obj), 201

    def get(self):
        """Retrieve all owner responses."""
        objects = facade.get_all_extended_resources("review_responses")
        return [serialize_review_response(obj) for obj in objects], 200


@responses_api.route("/<object_id>")
class ResponseResource(Resource):
    """Handle one owner response."""

    def get(self, object_id):
        """Retrieve an owner response."""
        return _get(
            "review_responses", object_id, "Review response",
            serialize_review_response
        )

    @responses_api.expect(response_update_model, validate=True)
    def put(self, object_id):
        """Update an owner response."""
        return _update(
            "review_responses", object_id, responses_api.payload or {},
            "Review response", serialize_review_response
        )


@guest_reviews_api.route("/")
class GuestReviewList(Resource):
    """Handle reviews written about booking guests."""

    @guest_reviews_api.expect(guest_review_model, validate=True)
    def post(self):
        """Create a review of a guest."""
        try:
            obj = facade.create_guest_review(guest_reviews_api.payload or {})
        except ValueError as exc:
            return {"error": str(exc)}, 400
        return serialize_guest_review(obj), 201

    def get(self):
        """Retrieve all guest reviews."""
        objects = facade.get_all_extended_resources("guest_reviews")
        return [serialize_guest_review(obj) for obj in objects], 200


@guest_reviews_api.route("/<object_id>")
class GuestReviewResource(Resource):
    """Handle one guest review."""

    def get(self, object_id):
        """Retrieve a guest review."""
        return _get(
            "guest_reviews", object_id, "Guest review",
            serialize_guest_review
        )

    @guest_reviews_api.expect(guest_review_update_model, validate=True)
    def put(self, object_id):
        """Update a guest review."""
        return _update(
            "guest_reviews", object_id, guest_reviews_api.payload or {},
            "Guest review", serialize_guest_review
        )
