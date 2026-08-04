#!/usr/bin/python3
"""Define system notification API endpoints."""

from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required

from app.api.v1.extended_helpers import serialize_notification
from app.services import facade


api = Namespace("notifications", description="System notification operations")

notification_model = api.model("SystemNotification", {
    "notification_type": fields.String(required=True),
    "content": fields.String(required=True),
    "user_id": fields.String(),
    "owner_id": fields.String()
})
notification_update_model = api.model("SystemNotificationUpdate", {
    "notification_type": fields.String(),
    "content": fields.String(),
    "is_seen": fields.Boolean()
})


def _admin_error():
    """Return an authorization response for a non-admin user."""
    if not get_jwt().get("is_admin", False):
        return {"error": "Admin privileges required"}, 403
    return None


def _notification_access_error(notification):
    """Allow an administrator or the notification's user recipient."""
    if get_jwt().get("is_admin", False):
        return None
    if notification.user is None:
        return {"error": "Unauthorized action"}, 403
    if notification.user.id != get_jwt_identity():
        return {"error": "Unauthorized action"}, 403
    return None


@api.route("/")
class NotificationList(Resource):
    """Handle the notification collection."""

    @api.expect(notification_model, validate=True)
    @jwt_required()
    def post(self):
        """Create a notification."""
        error = _admin_error()
        if error:
            return error
        try:
            notification = facade.create_notification(api.payload or {})
        except ValueError as exc:
            return {"error": str(exc)}, 400
        return serialize_notification(notification), 201

    @jwt_required()
    def get(self):
        """Retrieve all notifications."""
        notifications = facade.get_all_extended_resources("notifications")
        if not get_jwt().get("is_admin", False):
            user_id = get_jwt_identity()
            notifications = [
                notification for notification in notifications
                if notification.user is not None
                and notification.user.id == user_id
            ]
        return [
            serialize_notification(notification)
            for notification in notifications
        ], 200


@api.route("/<notification_id>")
class NotificationResource(Resource):
    """Handle one notification."""

    @jwt_required()
    def get(self, notification_id):
        """Retrieve a notification."""
        notification = facade.get_extended_resource(
            "notifications", notification_id
        )
        if notification is None:
            return {"error": "Notification not found"}, 404
        error = _notification_access_error(notification)
        if error:
            return error
        return serialize_notification(notification), 200

    @api.expect(notification_update_model, validate=True)
    @jwt_required()
    def put(self, notification_id):
        """Update a notification."""
        notification = facade.get_extended_resource(
            "notifications", notification_id
        )
        if notification is None:
            return {"error": "Notification not found"}, 404
        error = _notification_access_error(notification)
        if error:
            return error
        if (
            not get_jwt().get("is_admin", False)
            and set(api.payload or {}) - {"is_seen"}
        ):
            return {"error": "Unauthorized action"}, 403
        try:
            notification = facade.update_extended_resource(
                "notifications", notification_id, api.payload or {}
            )
        except ValueError as exc:
            return {"error": str(exc)}, 400
        if notification is None:
            return {"error": "Notification not found"}, 404
        return serialize_notification(notification), 200


@api.route("/<notification_id>/read")
class NotificationReadResource(Resource):
    """Handle the notification read action."""

    @jwt_required()
    def put(self, notification_id):
        """Mark a notification as read."""
        notification = facade.get_extended_resource(
            "notifications", notification_id
        )
        if notification is None:
            return {"error": "Notification not found"}, 404
        error = _notification_access_error(notification)
        if error:
            return error
        notification = facade.mark_notification_read(notification_id)
        return serialize_notification(notification), 200
