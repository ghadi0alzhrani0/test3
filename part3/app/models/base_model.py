#!/usr/bin/python3
"""Define the shared model behavior for HBnB entities."""

import uuid
from datetime import datetime


class BaseModel:
    """Provide common identifiers, timestamps, and update behavior."""

    def __init__(self):
        """Initialize common entity attributes."""
        self.id = str(uuid.uuid4())
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    def save(self):
        """Refresh the update timestamp."""
        self.updated_at = datetime.now()

    def update(self, data):
        """Update existing attributes from a dictionary."""
        protected = {"id", "created_at", "updated_at"}

        for key, value in data.items():
            if key not in protected and hasattr(self, key):
                setattr(self, key, value)

        self.save()
