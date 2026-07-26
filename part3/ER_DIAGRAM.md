# HBnB Database ER Diagram

```mermaid
erDiagram
    USER {
        string id PK
        string first_name
        string last_name
        string email UK
        string password
        boolean is_admin
        datetime created_at
        datetime updated_at
    }

    PLACE {
        string id PK
        string title
        text description
        decimal price
        float latitude
        float longitude
        string owner_id FK
        datetime created_at
        datetime updated_at
    }

    REVIEW {
        string id PK
        text text
        int rating
        string user_id FK
        string place_id FK
        datetime created_at
        datetime updated_at
    }

    AMENITY {
        string id PK
        string name UK
        datetime created_at
        datetime updated_at
    }

    PLACE_AMENITY {
        string place_id PK, FK
        string amenity_id PK, FK
    }

    USER ||--o{ PLACE : owns
    USER ||--o{ REVIEW : writes
    PLACE ||--o{ REVIEW : receives
    PLACE ||--o{ PLACE_AMENITY : contains
    AMENITY ||--o{ PLACE_AMENITY : belongs_to
```

The `PLACE_AMENITY` table implements the many-to-many relationship between
places and amenities. The combination of `user_id` and `place_id` is unique
in `REVIEW`, so one user can review a place only once.
