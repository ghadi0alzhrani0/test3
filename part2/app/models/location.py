#!/usr/bin/python3
"""Define country, state, and city business entities."""

from app.models.base_model import BaseModel


def _required_text(value, field, maximum=100):
    """Return a validated non-empty text value."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} is required")
    value = value.strip()
    if len(value) > maximum:
        raise ValueError(f"{field} must be {maximum} characters or fewer")
    return value


class Country(BaseModel):
    """Represent a country containing states."""

    def __init__(self, name, code):
        """Initialize a country."""
        super().__init__()
        self.name = _required_text(name, "Country name")
        self.code = _required_text(code, "Country code", 3).upper()
        self.states = []

    def add_state(self, state):
        """Attach a state to the country."""
        if state not in self.states:
            self.states.append(state)
            self.save()


class State(BaseModel):
    """Represent a state belonging to a country."""

    def __init__(self, name, country):
        """Initialize a state."""
        if not isinstance(country, Country):
            raise ValueError("Country must be valid")
        super().__init__()
        self.name = _required_text(name, "State name")
        self.country = country
        self.cities = []
        country.add_state(self)

    def add_city(self, city):
        """Attach a city to the state."""
        if city not in self.cities:
            self.cities.append(city)
            self.save()


class City(BaseModel):
    """Represent a city belonging to a state."""

    def __init__(self, name, state):
        """Initialize a city."""
        if not isinstance(state, State):
            raise ValueError("State must be valid")
        super().__init__()
        self.name = _required_text(name, "City name")
        self.state = state
        self.places = []
        state.add_city(self)

    def add_place(self, place):
        """Attach a place to the city."""
        if place not in self.places:
            self.places.append(place)
            self.save()
