#!/usr/bin/python3
"""Define amenity API endpoints."""

from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import get_jwt, jwt_required

from app.services import facade


api = Namespace("amenities", description="Amenity operations")

amenity_model = api.model("Amenity", {
    "name": fields.String(required=True, description="Name of the amenity"),
    "description": fields.String(description="Amenity description"),
    "category_id": fields.String(description="Amenity category ID")
})


def serialize_amenity(amenity):
    """Return a JSON-ready amenity dictionary."""
    return {
        "id": amenity.id,
        "name": amenity.name,
        "description": amenity.description,
        "category_id": amenity.category.id if amenity.category else None,
        "created_at": amenity.created_at.isoformat(),
        "updated_at": amenity.updated_at.isoformat()
    }


@api.route("/")
class AmenityList(Resource):
    """Handle operations for the amenity collection."""

    @jwt_required()
    @api.expect(amenity_model, validate=True)
    @api.response(201, "Amenity successfully created")
    @api.response(400, "Invalid input data")
    @api.response(403, "Admin privileges required")
    def post(self):
        """Register a new amenity."""
        if not get_jwt().get("is_admin", False):
            return {"error": "Admin privileges required"}, 403

        try:
            amenity = facade.create_amenity(api.payload or {})
        except ValueError as exc:
            return {"error": str(exc)}, 400

        return serialize_amenity(amenity), 201

    @api.response(200, "List of amenities retrieved successfully")
    def get(self):
        """Retrieve all amenities."""
        amenities = facade.get_all_amenities()
        return [serialize_amenity(amenity) for amenity in amenities], 200


@api.route("/<amenity_id>")
class AmenityResource(Resource):
    """Handle operations for a single amenity."""

    @api.response(200, "Amenity details retrieved successfully")
    @api.response(404, "Amenity not found")
    def get(self, amenity_id):
        """Retrieve amenity details by ID."""
        amenity = facade.get_amenity(amenity_id)
        if not amenity:
            return {"error": "Amenity not found"}, 404

        return serialize_amenity(amenity), 200

    @jwt_required()
    @api.expect(amenity_model, validate=True)
    @api.response(200, "Amenity updated successfully")
    @api.response(404, "Amenity not found")
    @api.response(400, "Invalid input data")
    @api.response(403, "Admin privileges required")
    def put(self, amenity_id):
        """Update amenity details."""
        if not get_jwt().get("is_admin", False):
            return {"error": "Admin privileges required"}, 403

        try:
            amenity = facade.update_amenity(amenity_id, api.payload or {})
        except ValueError as exc:
            return {"error": str(exc)}, 400

        if not amenity:
            return {"error": "Amenity not found"}, 404

        return serialize_amenity(amenity), 200
