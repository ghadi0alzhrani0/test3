#!/usr/bin/python3
"""Define the endpoint used to verify JWT authentication."""

from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restx import Namespace, Resource


api = Namespace("protected", description="Protected operations")


@api.route("")
class ProtectedResource(Resource):
    """Provide a simple JWT-protected resource."""

    @jwt_required()
    @api.response(200, "JWT is valid")
    def get(self):
        """Return the identity stored in a valid access token."""
        current_user = get_jwt_identity()
        return {"message": f"Hello, user {current_user}"}, 200
