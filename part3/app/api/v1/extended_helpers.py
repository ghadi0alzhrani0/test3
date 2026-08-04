#!/usr/bin/python3
"""Serialize the extended entities designed in Part 1."""


def _iso(value):
    """Return an ISO string for a date or datetime value."""
    return value.isoformat() if value is not None else None


def _base(obj):
    """Return fields shared by every business entity."""
    return {
        "id": obj.id,
        "created_at": _iso(obj.created_at),
        "updated_at": _iso(obj.updated_at)
    }


def serialize_owner(owner):
    """Return a business owner without exposing the password."""
    data = _base(owner)
    data.update({
        "business_name": owner.business_name,
        "contact_person": owner.contact_person,
        "email": owner.email,
        "phone_number": owner.phone_number,
        "commercial_register": owner.commercial_register
    })
    return data


def serialize_country(country):
    """Return country data and its state identifiers."""
    data = _base(country)
    data.update({
        "name": country.name,
        "code": country.code,
        "state_ids": [state.id for state in country.states]
    })
    return data


def serialize_state(state):
    """Return state data and its relationship identifiers."""
    data = _base(state)
    data.update({
        "name": state.name,
        "country_id": state.country.id,
        "city_ids": [city.id for city in state.cities]
    })
    return data


def serialize_city(city):
    """Return city data and its state identifier."""
    data = _base(city)
    data.update({"name": city.name, "state_id": city.state.id})
    return data


def serialize_place_type(place_type):
    """Return place type data."""
    data = _base(place_type)
    data["name"] = place_type.name
    return data


def serialize_policy(policy):
    """Return cancellation policy data."""
    data = _base(policy)
    data.update({"name": policy.name, "description": policy.description})
    return data


def serialize_category(category):
    """Return amenity category data."""
    data = _base(category)
    data.update({
        "name": category.name,
        "amenity_ids": [amenity.id for amenity in category.amenities]
    })
    return data


def serialize_room(room):
    """Return room detail data."""
    data = _base(room)
    data.update({
        "place_id": room.place.id,
        "room_name": room.room_name,
        "bed_type": room.bed_type,
        "beds_count": room.beds_count
    })
    return data


def serialize_availability(period):
    """Return a place availability period."""
    data = _base(period)
    data.update({
        "place_id": period.place.id,
        "start_date": _iso(period.start_date),
        "end_date": _iso(period.end_date),
        "is_booked": period.is_booked
    })
    return data


def serialize_pricing(pricing):
    """Return seasonal pricing data."""
    data = _base(pricing)
    data.update({
        "place_id": pricing.place.id,
        "start_date": _iso(pricing.start_date),
        "end_date": _iso(pricing.end_date),
        "special_price": pricing.special_price
    })
    return data


def serialize_booking(booking):
    """Return booking data and related record identifiers."""
    data = _base(booking)
    data.update({
        "place_id": booking.place.id,
        "user_id": booking.user.id,
        "start_date": _iso(booking.start_date),
        "end_date": _iso(booking.end_date),
        "total_price": booking.total_price,
        "status": booking.status,
        "guest_details_id": (
            booking.guest_details.id if booking.guest_details else None
        ),
        "history_ids": [item.id for item in booking.history]
    })
    return data


def serialize_booking_guest(details):
    """Return booking guest counts."""
    data = _base(details)
    data.update({
        "booking_id": details.booking.id,
        "adults_count": details.adults_count,
        "children_count": details.children_count,
        "infants_count": details.infants_count,
        "total_guests": details.get_total_guests_count()
    })
    return data


def serialize_booking_history(history):
    """Return one booking status change."""
    data = _base(history)
    data.update({
        "booking_id": history.booking.id,
        "old_status": history.old_status,
        "new_status": history.new_status,
        "changed_at": _iso(history.changed_at)
    })
    return data


def serialize_rating_details(details):
    """Return detailed category ratings for a review."""
    data = _base(details)
    data.update({
        "review_id": details.review.id,
        "cleanliness": details.cleanliness,
        "accuracy": details.accuracy,
        "communication": details.communication,
        "location": details.location,
        "check_in": details.check_in,
        "value": details.value,
        "average_rating": details.calculate_average_rating()
    })
    return data


def serialize_review_response(response):
    """Return a business owner's response to a review."""
    data = _base(response)
    data.update({
        "review_id": response.review.id,
        "owner_id": response.owner.id,
        "response_text": response.response_text
    })
    return data


def serialize_guest_review(review):
    """Return a business owner's review of a guest."""
    data = _base(review)
    data.update({
        "booking_id": review.booking.id,
        "owner_id": review.owner.id,
        "guest_id": review.guest.id,
        "cleanliness_rating": review.cleanliness_rating,
        "communication_rating": review.communication_rating,
        "respect_rules_rating": review.respect_rules_rating,
        "review_text": review.review_text
    })
    return data


def serialize_notification(notification):
    """Return system notification data."""
    data = _base(notification)
    data.update({
        "notification_type": notification.notification_type,
        "content": notification.content,
        "user_id": notification.user.id if notification.user else None,
        "owner_id": notification.owner.id if notification.owner else None,
        "is_seen": notification.is_seen
    })
    return data
