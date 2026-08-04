#!/usr/bin/python3
"""Define API endpoints for extended place details."""

from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required

from app.api.v1.extended_helpers import (
    serialize_availability,
    serialize_place_type,
    serialize_policy,
    serialize_pricing,
    serialize_room
)
from app.services import facade


place_types_api = Namespace("place-types", description="Place type operations")
policies_api = Namespace(
    "cancellation-policies",
    description="Cancellation policy operations"
)
rooms_api = Namespace("room-details", description="Room detail operations")
availability_api = Namespace(
    "place-availability",
    description="Place availability operations"
)
pricing_api = Namespace(
    "seasonal-pricing",
    description="Seasonal pricing operations"
)

place_type_model = place_types_api.model("PlaceType", {
    "name": fields.String(required=True)
})
place_type_update_model = place_types_api.model("PlaceTypeUpdate", {
    "name": fields.String()
})
policy_model = policies_api.model("CancellationPolicy", {
    "name": fields.String(required=True),
    "description": fields.String(required=True)
})
policy_update_model = policies_api.model("CancellationPolicyUpdate", {
    "name": fields.String(),
    "description": fields.String()
})
room_model = rooms_api.model("RoomDetail", {
    "place_id": fields.String(required=True),
    "room_name": fields.String(required=True),
    "bed_type": fields.String(required=True),
    "beds_count": fields.Integer(required=True)
})
room_update_model = rooms_api.model("RoomDetailUpdate", {
    "room_name": fields.String(),
    "bed_type": fields.String(),
    "beds_count": fields.Integer()
})
availability_model = availability_api.model("PlaceAvailability", {
    "place_id": fields.String(required=True),
    "start_date": fields.String(required=True, example="2026-08-10"),
    "end_date": fields.String(required=True, example="2026-08-15"),
    "is_booked": fields.Boolean()
})
availability_update_model = availability_api.model(
    "PlaceAvailabilityUpdate",
    {
        "start_date": fields.String(example="2026-08-10"),
        "end_date": fields.String(example="2026-08-15"),
        "is_booked": fields.Boolean()
    }
)
pricing_model = pricing_api.model("SeasonalPricing", {
    "place_id": fields.String(required=True),
    "start_date": fields.String(required=True, example="2026-12-20"),
    "end_date": fields.String(required=True, example="2027-01-05"),
    "special_price": fields.Float(required=True)
})
pricing_update_model = pricing_api.model("SeasonalPricingUpdate", {
    "start_date": fields.String(example="2026-12-20"),
    "end_date": fields.String(example="2027-01-05"),
    "special_price": fields.Float()
})


def _admin_error():
    """Return an authorization response for a non-admin user."""
    if not get_jwt().get("is_admin", False):
        return {"error": "Admin privileges required"}, 403
    return None


def _place_access_error(place_id):
    """Allow a place owner or administrator to manage place details."""
    place = facade.get_place(place_id)
    if place is None:
        return {"error": "Place not found"}, 404
    if (
        not get_jwt().get("is_admin", False)
        and place.owner.id != get_jwt_identity()
    ):
        return {"error": "Unauthorized action"}, 403
    return None


def _resource_access_error(resource, object_id, label):
    """Check ownership through an extended object's related place."""
    obj = facade.get_extended_resource(resource, object_id)
    if obj is None:
        return {"error": f"{label} not found"}, 404
    return _place_access_error(obj.place.id)


def _get(resource, object_id, label, serializer):
    """Return one extended place resource or a 404 response."""
    obj = facade.get_extended_resource(resource, object_id)
    if obj is None:
        return {"error": f"{label} not found"}, 404
    return serializer(obj), 200


def _update(resource, object_id, payload, label, serializer):
    """Update one extended place resource."""
    try:
        obj = facade.update_extended_resource(resource, object_id, payload)
    except ValueError as exc:
        return {"error": str(exc)}, 400
    if obj is None:
        return {"error": f"{label} not found"}, 404
    return serializer(obj), 200


@place_types_api.route("/")
class PlaceTypeList(Resource):
    """Handle the place type collection."""

    @place_types_api.expect(place_type_model, validate=True)
    @jwt_required()
    def post(self):
        """Create a place type."""
        error = _admin_error()
        if error:
            return error
        try:
            obj = facade.create_place_type(place_types_api.payload or {})
        except ValueError as exc:
            return {"error": str(exc)}, 400
        return serialize_place_type(obj), 201

    def get(self):
        """Retrieve all place types."""
        objects = facade.get_all_extended_resources("place_types")
        return [serialize_place_type(obj) for obj in objects], 200


@place_types_api.route("/<object_id>")
class PlaceTypeResource(Resource):
    """Handle one place type."""

    def get(self, object_id):
        """Retrieve a place type."""
        return _get(
            "place_types", object_id, "Place type", serialize_place_type
        )

    @place_types_api.expect(place_type_update_model, validate=True)
    @jwt_required()
    def put(self, object_id):
        """Update a place type."""
        error = _admin_error()
        if error:
            return error
        return _update(
            "place_types",
            object_id,
            place_types_api.payload or {},
            "Place type",
            serialize_place_type
        )


@policies_api.route("/")
class PolicyList(Resource):
    """Handle the cancellation policy collection."""

    @policies_api.expect(policy_model, validate=True)
    @jwt_required()
    def post(self):
        """Create a cancellation policy."""
        error = _admin_error()
        if error:
            return error
        try:
            obj = facade.create_cancellation_policy(policies_api.payload or {})
        except ValueError as exc:
            return {"error": str(exc)}, 400
        return serialize_policy(obj), 201

    def get(self):
        """Retrieve all cancellation policies."""
        objects = facade.get_all_extended_resources("cancellation_policies")
        return [serialize_policy(obj) for obj in objects], 200


@policies_api.route("/<object_id>")
class PolicyResource(Resource):
    """Handle one cancellation policy."""

    def get(self, object_id):
        """Retrieve a cancellation policy."""
        return _get(
            "cancellation_policies", object_id, "Policy", serialize_policy
        )

    @policies_api.expect(policy_update_model, validate=True)
    @jwt_required()
    def put(self, object_id):
        """Update a cancellation policy."""
        error = _admin_error()
        if error:
            return error
        return _update(
            "cancellation_policies",
            object_id,
            policies_api.payload or {},
            "Policy",
            serialize_policy
        )


@rooms_api.route("/")
class RoomList(Resource):
    """Handle the room detail collection."""

    @rooms_api.expect(room_model, validate=True)
    @jwt_required()
    def post(self):
        """Create room details for a place."""
        payload = rooms_api.payload or {}
        error = _place_access_error(payload.get("place_id"))
        if error:
            return error
        try:
            obj = facade.create_room_detail(payload)
        except ValueError as exc:
            return {"error": str(exc)}, 400
        return serialize_room(obj), 201

    def get(self):
        """Retrieve all room details."""
        objects = facade.get_all_extended_resources("room_details")
        return [serialize_room(obj) for obj in objects], 200


@rooms_api.route("/<object_id>")
class RoomResource(Resource):
    """Handle one room detail record."""

    def get(self, object_id):
        """Retrieve room details."""
        return _get("room_details", object_id, "Room detail", serialize_room)

    @rooms_api.expect(room_update_model, validate=True)
    @jwt_required()
    def put(self, object_id):
        """Update room details."""
        error = _resource_access_error(
            "room_details", object_id, "Room detail"
        )
        if error:
            return error
        return _update(
            "room_details",
            object_id,
            rooms_api.payload or {},
            "Room detail",
            serialize_room
        )


@availability_api.route("/")
class AvailabilityList(Resource):
    """Handle the availability collection."""

    @availability_api.expect(availability_model, validate=True)
    @jwt_required()
    def post(self):
        """Create an availability period."""
        payload = availability_api.payload or {}
        error = _place_access_error(payload.get("place_id"))
        if error:
            return error
        try:
            obj = facade.create_place_availability(payload)
        except ValueError as exc:
            return {"error": str(exc)}, 400
        return serialize_availability(obj), 201

    def get(self):
        """Retrieve all availability periods."""
        objects = facade.get_all_extended_resources("availability")
        return [serialize_availability(obj) for obj in objects], 200


@availability_api.route("/<object_id>")
class AvailabilityResource(Resource):
    """Handle one availability period."""

    def get(self, object_id):
        """Retrieve an availability period."""
        return _get(
            "availability", object_id, "Availability", serialize_availability
        )

    @availability_api.expect(availability_update_model, validate=True)
    @jwt_required()
    def put(self, object_id):
        """Update an availability period."""
        error = _resource_access_error(
            "availability", object_id, "Availability"
        )
        if error:
            return error
        return _update(
            "availability",
            object_id,
            availability_api.payload or {},
            "Availability",
            serialize_availability
        )


@pricing_api.route("/")
class PricingList(Resource):
    """Handle the seasonal pricing collection."""

    @pricing_api.expect(pricing_model, validate=True)
    @jwt_required()
    def post(self):
        """Create a seasonal price."""
        payload = pricing_api.payload or {}
        error = _place_access_error(payload.get("place_id"))
        if error:
            return error
        try:
            obj = facade.create_seasonal_pricing(payload)
        except ValueError as exc:
            return {"error": str(exc)}, 400
        return serialize_pricing(obj), 201

    def get(self):
        """Retrieve all seasonal prices."""
        objects = facade.get_all_extended_resources("seasonal_pricing")
        return [serialize_pricing(obj) for obj in objects], 200


@pricing_api.route("/<object_id>")
class PricingResource(Resource):
    """Handle one seasonal price."""

    def get(self, object_id):
        """Retrieve a seasonal price."""
        return _get(
            "seasonal_pricing", object_id, "Seasonal price", serialize_pricing
        )

    @pricing_api.expect(pricing_update_model, validate=True)
    @jwt_required()
    def put(self, object_id):
        """Update a seasonal price."""
        error = _resource_access_error(
            "seasonal_pricing", object_id, "Seasonal price"
        )
        if error:
            return error
        return _update(
            "seasonal_pricing",
            object_id,
            pricing_api.payload or {},
            "Seasonal price",
            serialize_pricing
        )
