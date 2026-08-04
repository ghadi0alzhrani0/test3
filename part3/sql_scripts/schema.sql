PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
    id CHAR(36) PRIMARY KEY,
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    is_admin BOOLEAN NOT NULL DEFAULT FALSE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS owners (
    id CHAR(36) PRIMARY KEY,
    business_name VARCHAR(255) NOT NULL,
    contact_person VARCHAR(100) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    password VARCHAR(128) NOT NULL,
    phone_number VARCHAR(30) NOT NULL,
    commercial_register VARCHAR(50) NOT NULL UNIQUE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS countries (
    id CHAR(36) PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    code VARCHAR(3) NOT NULL UNIQUE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS states (
    id CHAR(36) PRIMARY KEY,
    country_id CHAR(36) NOT NULL,
    name VARCHAR(100) NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (country_id) REFERENCES countries(id) ON DELETE CASCADE,
    UNIQUE (country_id, name)
);

CREATE TABLE IF NOT EXISTS cities (
    id CHAR(36) PRIMARY KEY,
    state_id CHAR(36) NOT NULL,
    name VARCHAR(100) NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (state_id) REFERENCES states(id) ON DELETE CASCADE,
    UNIQUE (state_id, name)
);

CREATE TABLE IF NOT EXISTS place_types (
    id CHAR(36) PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS cancellation_policies (
    id CHAR(36) PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS amenity_categories (
    id CHAR(36) PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS amenities (
    id CHAR(36) PRIMARY KEY,
    category_id CHAR(36),
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT NOT NULL DEFAULT '',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id)
        REFERENCES amenity_categories(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS places (
    id CHAR(36) PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    price DECIMAL(10, 2) NOT NULL CHECK (price >= 0),
    latitude FLOAT NOT NULL CHECK (latitude BETWEEN -90 AND 90),
    longitude FLOAT NOT NULL CHECK (longitude BETWEEN -180 AND 180),
    owner_id CHAR(36) NOT NULL,
    business_owner_id CHAR(36),
    city_id CHAR(36),
    place_type_id CHAR(36),
    cancellation_policy_id CHAR(36),
    number_rooms INT NOT NULL DEFAULT 0 CHECK (number_rooms >= 0),
    number_bathrooms INT NOT NULL DEFAULT 0 CHECK (number_bathrooms >= 0),
    max_guest INT NOT NULL DEFAULT 1 CHECK (max_guest >= 1),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (business_owner_id)
        REFERENCES owners(id) ON DELETE SET NULL,
    FOREIGN KEY (city_id) REFERENCES cities(id) ON DELETE SET NULL,
    FOREIGN KEY (place_type_id)
        REFERENCES place_types(id) ON DELETE SET NULL,
    FOREIGN KEY (cancellation_policy_id)
        REFERENCES cancellation_policies(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS room_details (
    id CHAR(36) PRIMARY KEY,
    place_id CHAR(36) NOT NULL,
    room_name VARCHAR(100) NOT NULL,
    bed_type VARCHAR(100) NOT NULL,
    beds_count INT NOT NULL CHECK (beds_count >= 1),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (place_id) REFERENCES places(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS place_availability (
    id CHAR(36) PRIMARY KEY,
    place_id CHAR(36) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    is_booked BOOLEAN NOT NULL DEFAULT FALSE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (place_id) REFERENCES places(id) ON DELETE CASCADE,
    CHECK (end_date > start_date)
);

CREATE TABLE IF NOT EXISTS seasonal_pricing (
    id CHAR(36) PRIMARY KEY,
    place_id CHAR(36) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    special_price DECIMAL(10, 2) NOT NULL CHECK (special_price >= 0),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (place_id) REFERENCES places(id) ON DELETE CASCADE,
    CHECK (end_date > start_date)
);

CREATE TABLE IF NOT EXISTS bookings (
    id CHAR(36) PRIMARY KEY,
    place_id CHAR(36) NOT NULL,
    user_id CHAR(36) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    total_price DECIMAL(10, 2) NOT NULL CHECK (total_price >= 0),
    status VARCHAR(20) NOT NULL DEFAULT 'pending'
        CHECK (status IN (
            'pending', 'confirmed', 'cancelled', 'checked_in', 'completed'
        )),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (place_id) REFERENCES places(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CHECK (end_date > start_date)
);

CREATE TABLE IF NOT EXISTS booking_guests (
    id CHAR(36) PRIMARY KEY,
    booking_id CHAR(36) NOT NULL UNIQUE,
    adults_count INT NOT NULL CHECK (adults_count >= 1),
    children_count INT NOT NULL DEFAULT 0 CHECK (children_count >= 0),
    infants_count INT NOT NULL DEFAULT 0 CHECK (infants_count >= 0),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (booking_id) REFERENCES bookings(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS booking_history (
    id CHAR(36) PRIMARY KEY,
    booking_id CHAR(36) NOT NULL,
    old_status VARCHAR(20) NOT NULL,
    new_status VARCHAR(20) NOT NULL,
    changed_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (booking_id) REFERENCES bookings(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS reviews (
    id CHAR(36) PRIMARY KEY,
    text TEXT NOT NULL,
    rating INT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    user_id CHAR(36) NOT NULL,
    place_id CHAR(36) NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (place_id) REFERENCES places(id) ON DELETE CASCADE,
    UNIQUE (user_id, place_id)
);

CREATE TABLE IF NOT EXISTS review_rating_details (
    id CHAR(36) PRIMARY KEY,
    review_id CHAR(36) NOT NULL UNIQUE,
    cleanliness INT NOT NULL CHECK (cleanliness BETWEEN 1 AND 5),
    accuracy INT NOT NULL CHECK (accuracy BETWEEN 1 AND 5),
    communication INT NOT NULL CHECK (communication BETWEEN 1 AND 5),
    location INT NOT NULL CHECK (location BETWEEN 1 AND 5),
    check_in INT NOT NULL CHECK (check_in BETWEEN 1 AND 5),
    value INT NOT NULL CHECK (value BETWEEN 1 AND 5),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (review_id) REFERENCES reviews(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS review_responses (
    id CHAR(36) PRIMARY KEY,
    review_id CHAR(36) NOT NULL UNIQUE,
    owner_id CHAR(36) NOT NULL,
    response_text TEXT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (review_id) REFERENCES reviews(id) ON DELETE CASCADE,
    FOREIGN KEY (owner_id) REFERENCES owners(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS guest_reviews (
    id CHAR(36) PRIMARY KEY,
    booking_id CHAR(36) NOT NULL UNIQUE,
    owner_id CHAR(36) NOT NULL,
    guest_id CHAR(36) NOT NULL,
    cleanliness_rating INT NOT NULL
        CHECK (cleanliness_rating BETWEEN 1 AND 5),
    communication_rating INT NOT NULL
        CHECK (communication_rating BETWEEN 1 AND 5),
    respect_rules_rating INT NOT NULL
        CHECK (respect_rules_rating BETWEEN 1 AND 5),
    review_text TEXT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (booking_id) REFERENCES bookings(id) ON DELETE CASCADE,
    FOREIGN KEY (owner_id) REFERENCES owners(id) ON DELETE CASCADE,
    FOREIGN KEY (guest_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS system_notifications (
    id CHAR(36) PRIMARY KEY,
    user_id CHAR(36),
    owner_id CHAR(36),
    notification_type VARCHAR(100) NOT NULL,
    content TEXT NOT NULL,
    is_seen BOOLEAN NOT NULL DEFAULT FALSE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (owner_id) REFERENCES owners(id) ON DELETE CASCADE,
    CHECK (user_id IS NOT NULL OR owner_id IS NOT NULL)
);

CREATE TABLE IF NOT EXISTS place_amenity (
    place_id CHAR(36) NOT NULL,
    amenity_id CHAR(36) NOT NULL,
    PRIMARY KEY (place_id, amenity_id),
    FOREIGN KEY (place_id) REFERENCES places(id) ON DELETE CASCADE,
    FOREIGN KEY (amenity_id) REFERENCES amenities(id) ON DELETE CASCADE
);
