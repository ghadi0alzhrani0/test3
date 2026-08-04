#!/usr/bin/python3
"""Define country, state, and city API endpoints."""

from flask_restx import Namespace, Resource, fields

from app.api.v1.extended_helpers import (
    serialize_city,
    serialize_country,
    serialize_state
)
from app.services import facade


countries_api = Namespace("countries", description="Country operations")
states_api = Namespace("states", description="State operations")
cities_api = Namespace("cities", description="City operations")

country_model = countries_api.model("Country", {
    "name": fields.String(required=True),
    "code": fields.String(required=True)
})
country_update_model = countries_api.model("CountryUpdate", {
    "name": fields.String(),
    "code": fields.String()
})
state_model = states_api.model("State", {
    "name": fields.String(required=True),
    "country_id": fields.String(required=True)
})
state_update_model = states_api.model("StateUpdate", {
    "name": fields.String()
})
city_model = cities_api.model("City", {
    "name": fields.String(required=True),
    "state_id": fields.String(required=True)
})
city_update_model = cities_api.model("CityUpdate", {
    "name": fields.String()
})


@countries_api.route("/")
class CountryList(Resource):
    """Handle the country collection."""

    @countries_api.expect(country_model, validate=True)
    def post(self):
        """Create a country."""
        try:
            country = facade.create_country(countries_api.payload or {})
        except ValueError as exc:
            return {"error": str(exc)}, 400
        return serialize_country(country), 201

    def get(self):
        """Retrieve all countries."""
        countries = facade.get_all_extended_resources("countries")
        return [serialize_country(country) for country in countries], 200


@countries_api.route("/<country_id>")
class CountryResource(Resource):
    """Handle one country."""

    def get(self, country_id):
        """Retrieve a country."""
        country = facade.get_extended_resource("countries", country_id)
        if country is None:
            return {"error": "Country not found"}, 404
        return serialize_country(country), 200

    @countries_api.expect(country_update_model, validate=True)
    def put(self, country_id):
        """Update a country."""
        try:
            country = facade.update_extended_resource(
                "countries", country_id, countries_api.payload or {}
            )
        except ValueError as exc:
            return {"error": str(exc)}, 400
        if country is None:
            return {"error": "Country not found"}, 404
        return serialize_country(country), 200


@states_api.route("/")
class StateList(Resource):
    """Handle the state collection."""

    @states_api.expect(state_model, validate=True)
    def post(self):
        """Create a state."""
        try:
            state = facade.create_state(states_api.payload or {})
        except ValueError as exc:
            return {"error": str(exc)}, 400
        return serialize_state(state), 201

    def get(self):
        """Retrieve all states."""
        states = facade.get_all_extended_resources("states")
        return [serialize_state(state) for state in states], 200


@states_api.route("/<state_id>")
class StateResource(Resource):
    """Handle one state."""

    def get(self, state_id):
        """Retrieve a state."""
        state = facade.get_extended_resource("states", state_id)
        if state is None:
            return {"error": "State not found"}, 404
        return serialize_state(state), 200

    @states_api.expect(state_update_model, validate=True)
    def put(self, state_id):
        """Update a state."""
        try:
            state = facade.update_extended_resource(
                "states", state_id, states_api.payload or {}
            )
        except ValueError as exc:
            return {"error": str(exc)}, 400
        if state is None:
            return {"error": "State not found"}, 404
        return serialize_state(state), 200


@cities_api.route("/")
class CityList(Resource):
    """Handle the city collection."""

    @cities_api.expect(city_model, validate=True)
    def post(self):
        """Create a city."""
        try:
            city = facade.create_city(cities_api.payload or {})
        except ValueError as exc:
            return {"error": str(exc)}, 400
        return serialize_city(city), 201

    def get(self):
        """Retrieve all cities."""
        cities = facade.get_all_extended_resources("cities")
        return [serialize_city(city) for city in cities], 200


@cities_api.route("/<city_id>")
class CityResource(Resource):
    """Handle one city."""

    def get(self, city_id):
        """Retrieve a city."""
        city = facade.get_extended_resource("cities", city_id)
        if city is None:
            return {"error": "City not found"}, 404
        return serialize_city(city), 200

    @cities_api.expect(city_update_model, validate=True)
    def put(self, city_id):
        """Update a city."""
        try:
            city = facade.update_extended_resource(
                "cities", city_id, cities_api.payload or {}
            )
        except ValueError as exc:
            return {"error": str(exc)}, 400
        if city is None:
            return {"error": "City not found"}, 404
        return serialize_city(city), 200
