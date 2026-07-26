#!/usr/bin/python3
"""Define user API endpoints."""

from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required

from app.services import facade


api = Namespace("users", description="User operations")

user_model = api.model("User", {
    "first_name": fields.String(required=True, description="First name"),
    "last_name": fields.String(required=True, description="Last name"),
    "email": fields.String(required=True, description="Email address"),
    "password": fields.String(required=True, description="Password")
})

user_update_model = api.model("UserUpdate", {
    "first_name": fields.String(description="First name"),
    "last_name": fields.String(description="Last name"),
    "email": fields.String(description="Email address"),
    "password": fields.String(description="Password"),
    "is_admin": fields.Boolean(description="Administrator status")
})


def serialize_user(user):
    """Return a JSON-ready user dictionary."""
    return {
        "id": user.id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email
    }


@api.route("/")
class UserList(Resource):
    """Handle operations for the user collection."""

    @jwt_required()
    @api.expect(user_model, validate=True)
    @api.response(201, "User successfully created")
    @api.response(400, "Invalid input data")
    @api.response(403, "Admin privileges required")
    def post(self):
        """Create a new user as an administrator."""
        if not get_jwt().get("is_admin", False):
            return {"error": "Admin privileges required"}, 403

        try:
            new_user = facade.create_user(api.payload or {})
        except ValueError as exc:
            return {"error": str(exc)}, 400

        return {
            "id": new_user.id,
            "message": "User registered successfully"
        }, 201

    @api.response(200, "List of users retrieved successfully")
    def get(self):
        """Retrieve all users."""
        return [serialize_user(user) for user in facade.get_all_users()], 200


@api.route("/<user_id>")
class UserResource(Resource):
    """Handle operations for a single user."""

    @api.response(200, "User details retrieved successfully")
    @api.response(404, "User not found")
    def get(self, user_id):
        """Retrieve user details by ID."""
        user = facade.get_user(user_id)
        if not user:
            return {"error": "User not found"}, 404

        return serialize_user(user), 200

    @jwt_required()
    @api.expect(user_update_model, validate=True)
    @api.response(200, "User updated successfully")
    @api.response(404, "User not found")
    @api.response(400, "Invalid input data")
    @api.response(403, "Unauthorized action")
    def put(self, user_id):
        """Update user details."""
        is_admin = get_jwt().get("is_admin", False)
        if not is_admin and get_jwt_identity() != user_id:
            return {"error": "Unauthorized action"}, 403

        data = api.payload or {}
        if not is_admin and ("email" in data or "password" in data):
            return {"error": "You cannot modify email or password"}, 400
        if not is_admin and "is_admin" in data:
            return {"error": "Admin privileges required"}, 403

        if is_admin and data.get("email"):
            existing_user = facade.get_user_by_email(data["email"])
            if existing_user and existing_user.id != user_id:
                return {"error": "Email already in use"}, 400

        try:
            user = facade.update_user(user_id, data)
        except ValueError as exc:
            return {"error": str(exc)}, 400

        if not user:
            return {"error": "User not found"}, 404

        return serialize_user(user), 200
