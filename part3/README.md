# HBnB Part 3 - Authentication and Database

## Description

This directory extends the HBnB business logic and REST API created in
Part 2. It adds password hashing, JWT authentication, role-based access
control, and persistent SQLite storage with SQLAlchemy.

The project keeps the same layered architecture:

- Presentation layer: Flask-RESTX API endpoints.
- Business Logic layer: User, Place, Review, and Amenity models.
- Service layer: HBnB Facade.
- Persistence layer: repository classes backed by SQLAlchemy.

## Main Features

- Password hashing with Flask-Bcrypt.
- Login with JWT access tokens.
- Authenticated user and administrator permissions.
- Ownership checks for places and reviews.
- SQLite persistence with Flask-SQLAlchemy.
- One-to-many and many-to-many entity relationships.
- SQL scripts for schema creation and initial data.
- Mermaid entity-relationship diagram.

## Project Structure

- `app/api/v1`: REST API endpoints.
- `app/models`: SQLAlchemy models and validation.
- `app/services`: Facade and specialized repositories.
- `app/persistence`: repository interface and implementations.
- `sql_scripts`: database schema and initial data.
- `tests`: automated API and persistence tests.
- `ER_DIAGRAM.md`: Mermaid database diagram.
- `ER_DIAGRAM.png`: Exported database diagram.
- `config.py`: application and database configuration.
- `run.py`: application entry point.

## Installation

```bash
python3 -m pip install -r requirements.txt
```

## Database Initialization

Create the mapped tables:

```bash
flask --app run.py shell
```

Then run:

```python
from app import db
db.create_all()
exit()
```

Load the initial administrator and amenities:

```bash
sqlite3 instance/development.db < sql_scripts/seed.sql
```

The initial administrator credentials are:

```text
Email: admin@hbnb.io
Password: admin1234
```

The password is stored as a bcrypt hash, not as plaintext.

## Running the Application

```bash
python3 run.py
```

Swagger documentation is available at:

```text
http://127.0.0.1:5000/api/v1/
```

## Authentication

Log in with:

```http
POST /api/v1/auth/login
```

Protected requests must include:

```text
Authorization: Bearer <access_token>
```

The JWT can be checked with:

```http
GET /api/v1/protected
```

Public users can retrieve places. Authenticated users can manage their
own profile, places, and reviews. Administrators can manage users and
amenities and can bypass place and review ownership restrictions.

## Running Tests

```bash
python3 -m unittest discover -s tests -v
```

See `TESTING.md` for the test coverage and manual verification commands.
