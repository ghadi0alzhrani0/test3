# HBnB Part 2 - Business Logic and REST API

## Description

This directory contains the Part 2 implementation of the HBnB project.
It follows the required layered architecture from the project rubric:
Presentation, Business Logic, Services, and Persistence.

The application uses Flask, Flask-RESTX, the Facade pattern, and an
in-memory repository. The repository is intentionally temporary for Part
2 and is designed to be replaced by SQLAlchemy persistence in Part 3.

## Project Structure

- `app/api/v1`: REST endpoints for users, amenities, places, and reviews.
- `app/models`: Business entities and validation logic.
- `app/services`: Facade that coordinates models and repositories.
- `app/persistence`: Abstract repository and in-memory implementation.
- `config.py`: Application configuration.
- `run.py`: Application entry point.
- `requirements.txt`: Python dependencies.
- `tests`: Unit tests for the API endpoints.
- `TESTING.md`: Manual and automated testing report.

## Implemented Entities

- `User`: first name, last name, email, admin flag, timestamps, and UUID.
- `Amenity`: name, timestamps, and UUID.
- `Place`: title, description, price, coordinates, owner, amenities,
  reviews, timestamps, and UUID.
- `Review`: text, rating, user, place, timestamps, and UUID.

Validation is implemented in the model layer. Invalid input raises
`ValueError` and the API converts it to a `400 Bad Request` response.

## Installation

```bash
python3 -m pip install -r requirements.txt
```

## Running the Application

```bash
python3 run.py
```

The application runs at:

```text
http://127.0.0.1:5000
```

Swagger documentation is available at:

```text
http://127.0.0.1:5000/api/v1/
```

## API Endpoints

- `POST /api/v1/users/`
- `GET /api/v1/users/`
- `GET /api/v1/users/<user_id>`
- `PUT /api/v1/users/<user_id>`
- `POST /api/v1/amenities/`
- `GET /api/v1/amenities/`
- `GET /api/v1/amenities/<amenity_id>`
- `PUT /api/v1/amenities/<amenity_id>`
- `POST /api/v1/places/`
- `GET /api/v1/places/`
- `GET /api/v1/places/<place_id>`
- `PUT /api/v1/places/<place_id>`
- `GET /api/v1/places/<place_id>/reviews`
- `POST /api/v1/reviews/`
- `GET /api/v1/reviews/`
- `GET /api/v1/reviews/<review_id>`
- `PUT /api/v1/reviews/<review_id>`
- `DELETE /api/v1/reviews/<review_id>`

## Running Tests

```bash
python3 -m unittest discover -s tests
```

See `TESTING.md` for the cURL test plan, validation cases, and testing
summary.

## Current Persistence

Part 2 uses an in-memory repository. Stored data exists only while the
application is running and will be lost when the server stops.

The repository will be replaced by a database-backed implementation in
Part 3.
