#!/usr/bin/python3
"""Define business owner API endpoints."""

from flask_restx import Namespace, Resource, fields

from app.api.v1.extended_helpers import serialize_owner
from app.services import facade


api = Namespace("owners", description="Business owner operations")

owner_model = api.model("Owner", {
    "business_name": fields.String(required=True),
    "contact_person": fields.String(required=True),
    "email": fields.String(required=True),
    "password": fields.String(required=True),
    "phone_number": fields.String(required=True),
    "commercial_register": fields.String(required=True)
})

owner_update_model = api.model("OwnerUpdate", {
    "business_name": fields.String(),
    "contact_person": fields.String(),
    "email": fields.String(),
    "password": fields.String(),
    "phone_number": fields.String(),
    "commercial_register": fields.String()
})


@api.route("/")
class OwnerList(Resource):
    """Handle the business owner collection."""

    @api.expect(owner_model, validate=True)
    def post(self):
        """Create a business owner."""
        try:
            owner = facade.create_owner(api.payload or {})
        except ValueError as exc:
            return {"error": str(exc)}, 400
        return serialize_owner(owner), 201

    def get(self):
        """Retrieve every business owner."""
        owners = facade.get_all_extended_resources("owners")
        return [serialize_owner(owner) for owner in owners], 200


@api.route("/<owner_id>")
class OwnerResource(Resource):
    """Handle one business owner."""

    def get(self, owner_id):
        """Retrieve a business owner."""
        owner = facade.get_extended_resource("owners", owner_id)
        if owner is None:
            return {"error": "Owner not found"}, 404
        return serialize_owner(owner), 200

    @api.expect(owner_update_model, validate=True)
    def put(self, owner_id):
        """Update a business owner."""
        try:
            owner = facade.update_extended_resource(
                "owners", owner_id, api.payload or {}
            )
        except ValueError as exc:
            return {"error": str(exc)}, 400
        if owner is None:
            return {"error": "Owner not found"}, 404
        return serialize_owner(owner), 200
