#!/usr/bin/python3
"""Define repository interfaces and persistence implementations."""

from abc import ABC, abstractmethod

from app import db


class Repository(ABC):
    """Define the required methods for repository classes."""

    @abstractmethod
    def add(self, obj):
        """Add an object to the repository."""
        pass

    @abstractmethod
    def get(self, obj_id):
        """Retrieve an object by its ID."""
        pass

    @abstractmethod
    def get_all(self):
        """Retrieve all stored objects."""
        pass

    @abstractmethod
    def update(self, obj_id, data):
        """Update an object using the provided data."""
        pass

    @abstractmethod
    def delete(self, obj_id):
        """Delete an object by its ID."""
        pass

    @abstractmethod
    def get_by_attribute(self, attr_name, attr_value):
        """Retrieve an object by one of its attributes."""
        pass


class InMemoryRepository(Repository):
    """Store and manage objects in memory."""

    def __init__(self):
        """Initialize an empty in-memory storage dictionary."""
        self._storage = {}

    def add(self, obj):
        """Add an object using its ID as the dictionary key."""
        self._storage[obj.id] = obj

    def get(self, obj_id):
        """Retrieve an object by its ID."""
        return self._storage.get(obj_id)

    def get_all(self):
        """Return all stored objects as a list."""
        return list(self._storage.values())

    def update(self, obj_id, data):
        """Update an existing object."""
        obj = self.get(obj_id)

        if obj is not None:
            obj.update(data)

    def delete(self, obj_id):
        """Delete an object if it exists."""
        if obj_id in self._storage:
            del self._storage[obj_id]

    def get_by_attribute(self, attr_name, attr_value):
        """Retrieve the first object matching an attribute value."""
        return next(
            (
                obj
                for obj in self._storage.values()
                if getattr(obj, attr_name, None) == attr_value
            ),
            None
        )


class SQLAlchemyRepository(Repository):
    """Store and manage mapped objects with SQLAlchemy."""

    def __init__(self, model):
        """Set the SQLAlchemy model managed by the repository."""
        self.model = model

    def add(self, obj):
        """Add and commit an object."""
        db.session.add(obj)
        db.session.commit()

    def get(self, obj_id):
        """Retrieve an object by its ID."""
        return db.session.get(self.model, obj_id)

    def get_all(self):
        """Return all stored objects."""
        return self.model.query.all()

    def update(self, obj_id, data):
        """Update and commit an object."""
        obj = self.get(obj_id)
        if obj:
            obj.update(data)
            db.session.commit()
        return obj

    def delete(self, obj_id):
        """Delete and commit an object."""
        obj = self.get(obj_id)
        if obj:
            db.session.delete(obj)
            db.session.commit()
        return obj

    def get_by_attribute(self, attr_name, attr_value):
        """Retrieve the first object matching an attribute."""
        return self.model.query.filter_by(
            **{attr_name: attr_value}
        ).first()

    def get_by_attributes(self, **filters):
        """Retrieve the first object matching multiple attributes."""
        return self.model.query.filter_by(**filters).first()
