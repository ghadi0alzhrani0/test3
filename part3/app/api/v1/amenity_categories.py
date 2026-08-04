#!/usr/bin/python3
"""Define amenity category API endpoints."""

from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import get_jwt, jwt_required

from app.api.v1.extended_helpers import serialize_category
from app.services import facade


api = Namespace(
    "amenity-categories",
    description="Amenity category operations"
)

category_model = api.model("AmenityCategory", {
    "name": fields.String(required=True)
})
category_update_model = api.model("AmenityCategoryUpdate", {
    "name": fields.String()
})


def _admin_error():
    """Return an authorization response for a non-admin user."""
    if not get_jwt().get("is_admin", False):
        return {"error": "Admin privileges required"}, 403
    return None


@api.route("/")
class AmenityCategoryList(Resource):
    """Handle the amenity category collection."""

    @api.expect(category_model, validate=True)
    @jwt_required()
    def post(self):
        """Create an amenity category."""
        error = _admin_error()
        if error:
            return error
        try:
            category = facade.create_amenity_category(api.payload or {})
        except ValueError as exc:
            return {"error": str(exc)}, 400
        return serialize_category(category), 201

    def get(self):
        """Retrieve all amenity categories."""
        categories = facade.get_all_extended_resources("amenity_categories")
        return [serialize_category(category) for category in categories], 200


@api.route("/<category_id>")
class AmenityCategoryResource(Resource):
    """Handle one amenity category."""

    def get(self, category_id):
        """Retrieve an amenity category."""
        category = facade.get_extended_resource(
            "amenity_categories", category_id
        )
        if category is None:
            return {"error": "Amenity category not found"}, 404
        return serialize_category(category), 200

    @api.expect(category_update_model, validate=True)
    @jwt_required()
    def put(self, category_id):
        """Update an amenity category."""
        error = _admin_error()
        if error:
            return error
        try:
            category = facade.update_extended_resource(
                "amenity_categories", category_id, api.payload or {}
            )
        except ValueError as exc:
            return {"error": str(exc)}, 400
        if category is None:
            return {"error": "Amenity category not found"}, 404
        return serialize_category(category), 200
