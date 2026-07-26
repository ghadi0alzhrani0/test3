#!/usr/bin/python3
"""Define user-specific database queries."""

from app.models.user import User
from app.persistence.repository import SQLAlchemyRepository


class UserRepository(SQLAlchemyRepository):
    """Provide persistence operations specific to users."""

    def __init__(self):
        """Manage the User model."""
        super().__init__(User)

    def get_user_by_email(self, email):
        """Retrieve a user by normalized email."""
        return self.model.query.filter_by(email=email.lower()).first()
