# HBnB Part 3 Testing

## Automated Tests

The automated tests are in `tests/test_api.py`. They use a separate
in-memory SQLite database so development data is not changed.

Run the suite from the `part3` directory:

```bash
python3 -m unittest discover -s tests -v
```

The suite covers:

- bcrypt password hashing and verification.
- Password exclusion from API responses.
- Valid and invalid login attempts.
- JWT validation through the protected endpoint.
- JWT protection for write endpoints.
- Regular user ownership restrictions.
- Administrator-only user and amenity operations.
- Administrator ownership bypass.
- Public place retrieval.
- Duplicate review prevention.
- Model validation from Part 2.
- SQLAlchemy persistence and bidirectional relationships.
- Updated entity data and `updated_at` values in PUT responses.
- Swagger route generation.
- Extended Part 1 location, ownership, place detail, and booking entities.
- Detailed ratings, owner responses, guest reviews, and notifications.

The complete suite contains 19 tests. A successful run ends with:

```text
Ran 19 tests
OK
```

## SQL Script Validation

Create a separate database with the raw SQL scripts:

```bash
sqlite3 hbnb_test.db < sql_scripts/schema.sql
sqlite3 hbnb_test.db < sql_scripts/seed.sql
sqlite3 hbnb_test.db < sql_scripts/test_crud.sql
```

Verify the initial data:

```bash
sqlite3 hbnb_test.db \
  "SELECT email, is_admin FROM users;" \
  "SELECT name FROM amenities ORDER BY name;"
```

Expected administrator:

```text
admin@hbnb.io|1
```

Expected CRUD test output:

```text
place|SQL Test Place|125
review|Updated SQL review|4
booking|confirmed
tables tested|22
deleted notifications|0
```

`test_crud.sql` runs inside a transaction and finishes with `ROLLBACK`, so
the test rows do not remain in the database. It covers `INSERT`, `SELECT`,
`UPDATE`, and `DELETE` while foreign key checking is enabled.

The scripts also enforce:

- Unique user emails.
- Unique amenity names.
- Ratings between 1 and 5.
- One review per user and place.
- Valid foreign keys.
- A composite primary key for `place_amenity`.
- Date ordering and non-negative prices for bookings and seasonal pricing.
- One-to-one booking guest, review detail, response, and guest review rows.
- A required recipient for every system notification.

## Manual API Flow

Start the server:

```bash
python3 run.py
```

### Login

```bash
curl -X POST http://127.0.0.1:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@hbnb.io","password":"admin1234"}'
```

Copy the returned `access_token` and use it in protected requests.

### Check the JWT

```bash
curl http://127.0.0.1:5000/api/v1/protected \
  -H "Authorization: Bearer <access_token>"
```

Expected status: `200 OK`. Without the token, the endpoint returns
`401 Unauthorized`.

### Create a User as Admin

```bash
curl -X POST http://127.0.0.1:5000/api/v1/users/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <admin_token>" \
  -d '{
    "first_name":"Jane",
    "last_name":"Doe",
    "email":"jane@example.com",
    "password":"secret123"
  }'
```

Expected status: `201 Created`.

### Create a Place as an Authenticated User

```bash
curl -X POST http://127.0.0.1:5000/api/v1/places/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <user_token>" \
  -d '{
    "title":"Cozy Apartment",
    "description":"A nice place to stay",
    "price":100,
    "latitude":24.7,
    "longitude":46.7,
    "amenities":[]
  }'
```

The API gets `owner_id` from the JWT. A client cannot choose another
user as the owner.

### Public Place Retrieval

```bash
curl http://127.0.0.1:5000/api/v1/places/
curl http://127.0.0.1:5000/api/v1/places/<place_id>
```

These endpoints work without a JWT.

### Create a Review

```bash
curl -X POST http://127.0.0.1:5000/api/v1/reviews/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <user_token>" \
  -d '{
    "text":"Great stay",
    "rating":5,
    "place_id":"<place_id>"
  }'
```

The API rejects reviews of the user's own place and duplicate reviews.
