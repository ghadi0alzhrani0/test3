#!/usr/bin/python3
"""Define system notification API endpoints."""

from flask_restx import Namespace, Resource, fields

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


@api.route("/")
class NotificationList(Resource):
    """Handle the notification collection."""

    @api.expect(notification_model, validate=True)
    def post(self):
        """Create a notification."""
        try:
            notification = facade.create_notification(api.payload or {})
        except ValueError as exc:
            return {"error": str(exc)}, 400
        return serialize_notification(notification), 201

    def get(self):
        """Retrieve all notifications."""
        notifications = facade.get_all_extended_resources("notifications")
        return [
            serialize_notification(notification)
            for notification in notifications
        ], 200


@api.route("/<notification_id>")
class NotificationResource(Resource):
    """Handle one notification."""

    def get(self, notification_id):
        """Retrieve a notification."""
        notification = facade.get_extended_resource(
            "notifications", notification_id
        )
        if notification is None:
            return {"error": "Notification not found"}, 404
        return serialize_notification(notification), 200

    @api.expect(notification_update_model, validate=True)
    def put(self, notification_id):
        """Update a notification."""
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

    def put(self, notification_id):
        """Mark a notification as read."""
        notification = facade.mark_notification_read(notification_id)
        if notification is None:
            return {"error": "Notification not found"}, 404
        return serialize_notification(notification), 200
