#!/usr/bin/python3
"""Define system notifications from the Part 1 design."""

from app.models.base_model import BaseModel


class SystemNotification(BaseModel):
    """Represent a notification sent to a user or business owner."""

    def __init__(
        self,
        notification_type,
        content,
        user=None,
        owner=None,
        is_seen=False
    ):
        """Initialize a notification."""
        from app.models.owner import Owner
        from app.models.user import User

        if user is None and owner is None:
            raise ValueError("A notification recipient is required")
        if user is not None and not isinstance(user, User):
            raise ValueError("User must be valid")
        if owner is not None and not isinstance(owner, Owner):
            raise ValueError("Owner must be valid")
        if (
            not isinstance(notification_type, str)
            or not notification_type.strip()
        ):
            raise ValueError("Notification type is required")
        if not isinstance(content, str) or not content.strip():
            raise ValueError("Notification content is required")
        if not isinstance(is_seen, bool):
            raise ValueError("is_seen must be a boolean")
        super().__init__()
        self.notification_type = notification_type.strip()
        self.content = content.strip()
        self.user = user
        self.owner = owner
        self.is_seen = is_seen
        self.send_notification()

    def send_notification(self):
        """Attach the notification to its recipients."""
        if self.user is not None and self not in self.user.notifications:
            self.user.notifications.append(self)
        if self.owner is not None and self not in self.owner.notifications:
            self.owner.notifications.append(self)

    def mark_as_read(self):
        """Mark the notification as seen."""
        self.is_seen = True
        self.save()
