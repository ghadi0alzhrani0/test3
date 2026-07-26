PRAGMA foreign_keys = ON;

INSERT OR IGNORE INTO users (
    id,
    first_name,
    last_name,
    email,
    password,
    is_admin
) VALUES (
    '36c9050e-ddd3-4c3b-9731-9f487208bbc1',
    'Admin',
    'HBnB',
    'admin@hbnb.io',
    '$2b$12$zeuhQ.xNzO2vG7PZ.b8/z.pS13bby3ses.WExKypcAhTOd3.R.twu',
    TRUE
);

INSERT OR IGNORE INTO amenities (id, name)
VALUES ('88c9d062-eaff-4485-a494-b279317cd379', 'WiFi');

INSERT OR IGNORE INTO amenities (id, name)
VALUES ('c8bc96c8-ac00-4d0d-a903-f73677e2dc54', 'Swimming Pool');

INSERT OR IGNORE INTO amenities (id, name)
VALUES ('75d0eb05-2d07-463e-9c73-8592cd0c9be0', 'Air Conditioning');
