.bail on
PRAGMA foreign_keys = ON;

BEGIN TRANSACTION;

INSERT INTO users (
    id, first_name, last_name, email, password, is_admin
) VALUES (
    '10000000-0000-4000-8000-000000000001',
    'Test', 'Guest', 'sql.guest@example.com', 'test-hash', FALSE
);

INSERT INTO owners (
    id, business_name, contact_person, email, password,
    phone_number, commercial_register
) VALUES (
    '10000000-0000-4000-8000-000000000002',
    'SQL Stays', 'Test Owner', 'sql.owner@example.com', 'test-hash',
    '+966500000000', 'SQL-CR-1'
);

INSERT INTO countries (id, name, code) VALUES (
    '10000000-0000-4000-8000-000000000003', 'Test Country', 'TC'
);
INSERT INTO states (id, country_id, name) VALUES (
    '10000000-0000-4000-8000-000000000004',
    '10000000-0000-4000-8000-000000000003', 'Test State'
);
INSERT INTO cities (id, state_id, name) VALUES (
    '10000000-0000-4000-8000-000000000005',
    '10000000-0000-4000-8000-000000000004', 'Test City'
);
INSERT INTO place_types (id, name) VALUES (
    '10000000-0000-4000-8000-000000000006', 'Test Apartment'
);
INSERT INTO cancellation_policies (id, name, description) VALUES (
    '10000000-0000-4000-8000-000000000007',
    'Test Flexible', 'Full refund seven days before arrival'
);
INSERT INTO amenity_categories (id, name) VALUES (
    '10000000-0000-4000-8000-000000000008', 'Test Connectivity'
);
INSERT INTO amenities (id, category_id, name, description) VALUES (
    '10000000-0000-4000-8000-000000000009',
    '10000000-0000-4000-8000-000000000008',
    'Test Fiber', 'Test internet connection'
);

INSERT INTO places (
    id, title, description, price, latitude, longitude, owner_id,
    business_owner_id, city_id, place_type_id, cancellation_policy_id,
    number_rooms, number_bathrooms, max_guest
) VALUES (
    '10000000-0000-4000-8000-000000000010',
    'SQL Test Place', 'Created by test_crud.sql', 100, 24.7, 46.7,
    '10000000-0000-4000-8000-000000000001',
    '10000000-0000-4000-8000-000000000002',
    '10000000-0000-4000-8000-000000000005',
    '10000000-0000-4000-8000-000000000006',
    '10000000-0000-4000-8000-000000000007', 2, 1, 4
);
INSERT INTO place_amenity (place_id, amenity_id) VALUES (
    '10000000-0000-4000-8000-000000000010',
    '10000000-0000-4000-8000-000000000009'
);
INSERT INTO room_details (
    id, place_id, room_name, bed_type, beds_count
) VALUES (
    '10000000-0000-4000-8000-000000000011',
    '10000000-0000-4000-8000-000000000010',
    'Main bedroom', 'Queen', 1
);
INSERT INTO place_availability (
    id, place_id, start_date, end_date, is_booked
) VALUES (
    '10000000-0000-4000-8000-000000000012',
    '10000000-0000-4000-8000-000000000010',
    '2026-10-01', '2026-10-03', TRUE
);
INSERT INTO seasonal_pricing (
    id, place_id, start_date, end_date, special_price
) VALUES (
    '10000000-0000-4000-8000-000000000013',
    '10000000-0000-4000-8000-000000000010',
    '2026-12-01', '2026-12-31', 150
);

INSERT INTO bookings (
    id, place_id, user_id, start_date, end_date, total_price, status
) VALUES (
    '10000000-0000-4000-8000-000000000014',
    '10000000-0000-4000-8000-000000000010',
    '10000000-0000-4000-8000-000000000001',
    '2026-11-01', '2026-11-03', 200, 'pending'
);
INSERT INTO booking_guests (
    id, booking_id, adults_count, children_count, infants_count
) VALUES (
    '10000000-0000-4000-8000-000000000015',
    '10000000-0000-4000-8000-000000000014', 2, 1, 0
);
INSERT INTO booking_history (
    id, booking_id, old_status, new_status
) VALUES (
    '10000000-0000-4000-8000-000000000016',
    '10000000-0000-4000-8000-000000000014',
    'pending', 'confirmed'
);

INSERT INTO reviews (id, text, rating, user_id, place_id) VALUES (
    '10000000-0000-4000-8000-000000000017',
    'SQL review', 5,
    '10000000-0000-4000-8000-000000000001',
    '10000000-0000-4000-8000-000000000010'
);
INSERT INTO review_rating_details (
    id, review_id, cleanliness, accuracy, communication,
    location, check_in, value
) VALUES (
    '10000000-0000-4000-8000-000000000018',
    '10000000-0000-4000-8000-000000000017', 5, 4, 5, 4, 5, 4
);
INSERT INTO review_responses (
    id, review_id, owner_id, response_text
) VALUES (
    '10000000-0000-4000-8000-000000000019',
    '10000000-0000-4000-8000-000000000017',
    '10000000-0000-4000-8000-000000000002',
    'Thank you for the review'
);
INSERT INTO guest_reviews (
    id, booking_id, owner_id, guest_id, cleanliness_rating,
    communication_rating, respect_rules_rating, review_text
) VALUES (
    '10000000-0000-4000-8000-000000000020',
    '10000000-0000-4000-8000-000000000014',
    '10000000-0000-4000-8000-000000000002',
    '10000000-0000-4000-8000-000000000001', 5, 5, 5,
    'Respectful guest'
);
INSERT INTO system_notifications (
    id, user_id, notification_type, content
) VALUES (
    '10000000-0000-4000-8000-000000000021',
    '10000000-0000-4000-8000-000000000001',
    'booking_confirmed', 'Your booking is confirmed'
);

UPDATE places
SET price = 125, updated_at = CURRENT_TIMESTAMP
WHERE id = '10000000-0000-4000-8000-000000000010';
UPDATE reviews
SET text = 'Updated SQL review', rating = 4
WHERE id = '10000000-0000-4000-8000-000000000017';
UPDATE bookings
SET status = 'confirmed'
WHERE id = '10000000-0000-4000-8000-000000000014';

SELECT 'place', title, price FROM places
WHERE id = '10000000-0000-4000-8000-000000000010';
SELECT 'review', text, rating FROM reviews
WHERE id = '10000000-0000-4000-8000-000000000017';
SELECT 'booking', status FROM bookings
WHERE id = '10000000-0000-4000-8000-000000000014';
SELECT 'tables tested', COUNT(*) FROM sqlite_master
WHERE type = 'table' AND name NOT LIKE 'sqlite_%';

DELETE FROM system_notifications
WHERE id = '10000000-0000-4000-8000-000000000021';
SELECT 'deleted notifications', COUNT(*) FROM system_notifications
WHERE id = '10000000-0000-4000-8000-000000000021';

ROLLBACK;
