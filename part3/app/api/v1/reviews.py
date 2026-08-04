#!/usr/bin/python3
"""Define review API endpoints."""

from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required

from app.services import facade


api = Namespace("reviews", description="Review operations")

review_model = api.model("Review", {
    "text": fields.String(required=True, description="Text of the review"),
    "rating": fields.Integer(required=True, description="Rating from 1 to 5"),
    "place_id": fields.String(required=True, description="ID of the place")
})

review_update_model = api.model("ReviewUpdate", {
    "text": fields.String(description="Text of the review"),
    "rating": fields.Integer(description="Rating from 1 to 5")
})


def serialize_review(review, include_relationships=True):
    """Return a JSON-ready review dictionary."""
    data = {
        "id": review.id,
        "text": review.text,
        "rating": review.rating,
        "created_at": review.created_at.isoformat(),
        "updated_at": review.updated_at.isoformat()
    }

    if include_relationships:
        data["user_id"] = review.user.id
        data["place_id"] = review.place.id

    return data


@api.route("/")
class ReviewList(Resource):
    """Handle operations for the review collection."""

    @jwt_required()
    @api.expect(review_model, validate=True)
    @api.response(201, "Review successfully created")
    @api.response(400, "Invalid input data")
    def post(self):
        """Register a new review."""
        data = (api.payload or {}).copy()
        user_id = get_jwt_identity()
        place = facade.get_place(data.get("place_id"))
        is_admin = get_jwt().get("is_admin", False)

        if not place:
            return {"error": "Place not found"}, 400
        if not is_admin and place.owner.id == user_id:
            return {"error": "You cannot review your own place"}, 400
        if facade.get_review_by_user_and_place(user_id, place.id):
            return {"error": "You have already reviewed this place"}, 400

        data["user_id"] = user_id
        try:
            review = facade.create_review(data)
        except ValueError as exc:
            return {"error": str(exc)}, 400

        return serialize_review(review), 201

    @api.response(200, "List of reviews retrieved successfully")
    def get(self):
        """Retrieve all reviews."""
        reviews = facade.get_all_reviews()
        return [
            serialize_review(review, include_relationships=False)
            for review in reviews
        ], 200


@api.route("/<review_id>")
class ReviewResource(Resource):
    """Handle operations for a single review."""

    @api.response(200, "Review details retrieved successfully")
    @api.response(404, "Review not found")
    def get(self, review_id):
        """Retrieve review details by ID."""
        review = facade.get_review(review_id)
        if not review:
            return {"error": "Review not found"}, 404

        return serialize_review(review), 200

    @jwt_required()
    @api.expect(review_update_model, validate=True)
    @api.response(200, "Review updated successfully")
    @api.response(404, "Review not found")
    @api.response(400, "Invalid input data")
    @api.response(403, "Unauthorized action")
    def put(self, review_id):
        """Update review details."""
        review = facade.get_review(review_id)
        if not review:
            return {"error": "Review not found"}, 404
        is_admin = get_jwt().get("is_admin", False)
        if not is_admin and review.user.id != get_jwt_identity():
            return {"error": "Unauthorized action"}, 403

        try:
            review = facade.update_review(review_id, api.payload or {})
        except ValueError as exc:
            return {"error": str(exc)}, 400

        return serialize_review(review), 200

    @jwt_required()
    @api.response(200, "Review deleted successfully")
    @api.response(404, "Review not found")
    @api.response(403, "Unauthorized action")
    def delete(self, review_id):
        """Delete a review."""
        review = facade.get_review(review_id)
        if not review:
            return {"error": "Review not found"}, 404
        is_admin = get_jwt().get("is_admin", False)
        if not is_admin and review.user.id != get_jwt_identity():
            return {"error": "Unauthorized action"}, 403

        facade.delete_review(review_id)

        return {"message": "Review deleted successfully"}, 200
