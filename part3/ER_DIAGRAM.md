# HBnB Database ER Diagrams

## Required Core Schema

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

The exported version of the diagram is available in
[`ER_DIAGRAM.png`](ER_DIAGRAM.png).

## Extended HBnB Schema

The project keeps the additional entities designed in Part 1. They extend
the required schema without changing the required User, Place, Review,
Amenity, or Place_Amenity relationships.

```mermaid
erDiagram
    USER {
        string id PK
        string email UK
        string password
        boolean is_admin
    }
    OWNER {
        string id PK
        string business_name
        string email UK
        string commercial_register UK
    }
    COUNTRY {
        string id PK
        string name UK
        string code UK
    }
    STATE {
        string id PK
        string country_id FK
        string name
    }
    CITY {
        string id PK
        string state_id FK
        string name
    }
    PLACE_TYPE {
        string id PK
        string name UK
    }
    CANCELLATION_POLICY {
        string id PK
        string name UK
        text description
    }
    PLACE {
        string id PK
        string owner_id FK
        string business_owner_id FK
        string city_id FK
        string place_type_id FK
        string cancellation_policy_id FK
        string title
        decimal price
    }
    ROOM_DETAIL {
        string id PK
        string place_id FK
        string room_name
        string bed_type
        int beds_count
    }
    PLACE_AVAILABILITY {
        string id PK
        string place_id FK
        date start_date
        date end_date
        boolean is_booked
    }
    SEASONAL_PRICING {
        string id PK
        string place_id FK
        date start_date
        date end_date
        decimal special_price
    }
    AMENITY_CATEGORY {
        string id PK
        string name UK
    }
    AMENITY {
        string id PK
        string category_id FK
        string name UK
        text description
    }
    PLACE_AMENITY {
        string place_id PK, FK
        string amenity_id PK, FK
    }
    BOOKING {
        string id PK
        string place_id FK
        string user_id FK
        date start_date
        date end_date
        decimal total_price
        string status
    }
    BOOKING_GUEST {
        string id PK
        string booking_id FK, UK
        int adults_count
        int children_count
        int infants_count
    }
    BOOKING_HISTORY {
        string id PK
        string booking_id FK
        string old_status
        string new_status
        datetime changed_at
    }
    REVIEW {
        string id PK
        string user_id FK
        string place_id FK
        text text
        int rating
    }
    REVIEW_RATING_DETAILS {
        string id PK
        string review_id FK, UK
        int cleanliness
        int accuracy
        int communication
        int location
        int check_in
        int value
    }
    REVIEW_RESPONSE {
        string id PK
        string review_id FK, UK
        string owner_id FK
        text response_text
    }
    GUEST_REVIEW {
        string id PK
        string booking_id FK, UK
        string owner_id FK
        string guest_id FK
        int cleanliness_rating
        int communication_rating
        int respect_rules_rating
    }
    SYSTEM_NOTIFICATION {
        string id PK
        string user_id FK
        string owner_id FK
        string notification_type
        text content
        boolean is_seen
    }

    COUNTRY ||--o{ STATE : contains
    STATE ||--o{ CITY : contains
    CITY ||--o{ PLACE : locates
    USER ||--o{ PLACE : owns
    OWNER ||--o{ PLACE : manages
    PLACE_TYPE ||--o{ PLACE : classifies
    CANCELLATION_POLICY ||--o{ PLACE : controls
    PLACE ||--o{ ROOM_DETAIL : contains
    PLACE ||--o{ PLACE_AVAILABILITY : schedules
    PLACE ||--o{ SEASONAL_PRICING : prices
    AMENITY_CATEGORY ||--o{ AMENITY : groups
    PLACE ||--o{ PLACE_AMENITY : links
    AMENITY ||--o{ PLACE_AMENITY : links
    USER ||--o{ BOOKING : creates
    PLACE ||--o{ BOOKING : receives
    BOOKING ||--o| BOOKING_GUEST : describes
    BOOKING ||--o{ BOOKING_HISTORY : records
    USER ||--o{ REVIEW : writes
    PLACE ||--o{ REVIEW : receives
    REVIEW ||--o| REVIEW_RATING_DETAILS : details
    REVIEW ||--o| REVIEW_RESPONSE : receives
    OWNER ||--o{ REVIEW_RESPONSE : writes
    BOOKING ||--o| GUEST_REVIEW : receives
    OWNER ||--o{ GUEST_REVIEW : writes
    USER ||--o{ GUEST_REVIEW : receives
    USER ||--o{ SYSTEM_NOTIFICATION : receives
    OWNER ||--o{ SYSTEM_NOTIFICATION : receives
```
