#!/usr/bin/python3
"""Map country, state, and city entities with SQLAlchemy."""

from sqlalchemy.orm import validates

from app import db
from app.models.base_model import BaseModel


def _required_text(value, field, maximum=100):
    """Return validated required text."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} is required")
    value = value.strip()
    if len(value) > maximum:
        raise ValueError(f"{field} must be {maximum} characters or fewer")
    return value


class Country(BaseModel):
    """Represent a country containing states."""

    __tablename__ = "countries"

    name = db.Column(db.String(100), nullable=False, unique=True)
    code = db.Column(db.String(3), nullable=False, unique=True)
    states = db.relationship(
        "State",
        back_populates="country",
        cascade="all, delete-orphan"
    )

    def __init__(self, name, code):
        """Initialize a country."""
        super().__init__()
        self.name = name
        self.code = code

    @validates("name")
    def validate_name(self, key, value):
        """Validate the country name."""
        return _required_text(value, "Country name")

    @validates("code")
    def validate_code(self, key, value):
        """Validate and normalize the country code."""
        return _required_text(value, "Country code", 3).upper()


class State(BaseModel):
    """Represent a state belonging to a country."""

    __tablename__ = "states"
    __table_args__ = (
        db.UniqueConstraint(
            "country_id",
            "name",
            name="uq_state_country_name"
        ),
    )

    name = db.Column(db.String(100), nullable=False)
    country_id = db.Column(
        db.String(36),
        db.ForeignKey("countries.id"),
        nullable=False
    )
    country = db.relationship("Country", back_populates="states")
    cities = db.relationship(
        "City",
        back_populates="state",
        cascade="all, delete-orphan"
    )

    def __init__(self, name, country):
        """Initialize a state."""
        super().__init__()
        self.name = name
        self.country = country

    @validates("name")
    def validate_name(self, key, value):
        """Validate the state name."""
        return _required_text(value, "State name")


class City(BaseModel):
    """Represent a city belonging to a state."""

    __tablename__ = "cities"
    __table_args__ = (
        db.UniqueConstraint("state_id", "name", name="uq_city_state_name"),
    )

    name = db.Column(db.String(100), nullable=False)
    state_id = db.Column(
        db.String(36),
        db.ForeignKey("states.id"),
        nullable=False
    )
    state = db.relationship("State", back_populates="cities")
    places = db.relationship("Place", back_populates="city")

    def __init__(self, name, state):
        """Initialize a city."""
        super().__init__()
        self.name = name
        self.state = state

    @validates("name")
    def validate_name(self, key, value):
        """Validate the city name."""
        return _required_text(value, "City name")
