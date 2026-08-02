#!/usr/bin/python3
"""Define review API endpoints."""

from flask_restx import Namespace, Resource, fields

from app.services import facade


api = Namespace("reviews", description="Review operations")

review_model = api.model("Review", {
    "text": fields.String(required=True, description="Text of the review"),
    "rating": fields.Integer(required=True, description="Rating from 1 to 5"),
    "user_id": fields.String(required=True, description="ID of the user"),
    "place_id": fields.String(required=True, description="ID of the place")
})

review_update_model = api.model("ReviewUpdate", {
    "text": fields.String(description="Text of the review"),
    "rating": fields.Integer(description="Rating from 1 to 5"),
    "user_id": fields.String(description="ID of the user"),
    "place_id": fields.String(description="ID of the place")
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

    @api.expect(review_model, validate=True)
    @api.response(201, "Review successfully created")
    @api.response(400, "Invalid input data")
    def post(self):
        """Register a new review."""
        try:
            review = facade.create_review(api.payload or {})
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

    @api.expect(review_update_model, validate=True)
    @api.response(200, "Review updated successfully")
    @api.response(404, "Review not found")
    @api.response(400, "Invalid input data")
    def put(self, review_id):
        """Update review details."""
        try:
            review = facade.update_review(review_id, api.payload or {})
        except ValueError as exc:
            return {"error": str(exc)}, 400

        if not review:
            return {"error": "Review not found"}, 404

        return serialize_review(review), 200

    @api.response(200, "Review deleted successfully")
    @api.response(404, "Review not found")
    def delete(self, review_id):
        """Delete a review."""
        deleted = facade.delete_review(review_id)
        if not deleted:
            return {"error": "Review not found"}, 404

        return {"message": "Review deleted successfully"}, 200
