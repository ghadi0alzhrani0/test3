#!/usr/bin/python3
"""Map system notifications with SQLAlchemy."""

from sqlalchemy.orm import validates

from app import db
from app.models.base_model import BaseModel


class SystemNotification(BaseModel):
    """Represent a notification sent to a user or business owner."""

    __tablename__ = "system_notifications"
    __table_args__ = (
        db.CheckConstraint(
            "user_id IS NOT NULL OR owner_id IS NOT NULL",
            name="ck_notification_recipient"
        ),
    )

    user_id = db.Column(
        db.String(36),
        db.ForeignKey("users.id"),
        nullable=True
    )
    owner_id = db.Column(
        db.String(36),
        db.ForeignKey("owners.id"),
        nullable=True
    )
    notification_type = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    is_seen = db.Column(db.Boolean, default=False, nullable=False)

    user = db.relationship("User", back_populates="notifications")
    owner = db.relationship("Owner", back_populates="notifications")

    def __init__(
        self,
        notification_type,
        content,
        user=None,
        owner=None,
        is_seen=False
    ):
        """Initialize a notification."""
        if user is None and owner is None:
            raise ValueError("A notification recipient is required")
        super().__init__()
        self.notification_type = notification_type
        self.content = content
        self.user = user
        self.owner = owner
        self.is_seen = is_seen

    @validates("notification_type", "content")
    def validate_text(self, key, value):
        """Validate notification text."""
        if not isinstance(value, str) or not value.strip():
            label = (
                "Notification type"
                if key == "notification_type"
                else "Content"
            )
            raise ValueError(f"{label} is required")
        return value.strip()

    @validates("is_seen")
    def validate_is_seen(self, key, value):
        """Validate the seen flag."""
        if not isinstance(value, bool):
            raise ValueError("is_seen must be a boolean")
        return value

    def send_notification(self):
        """Return the notification recipient identifiers."""
        return {
            "user_id": self.user_id,
            "owner_id": self.owner_id
        }

    def mark_as_read(self):
        """Mark the notification as seen."""
        self.is_seen = True
        self.save()
