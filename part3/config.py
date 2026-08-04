#!/usr/bin/python3
"""Define configuration classes for the HBnB application."""

import os


class Config:
    """Define common application configuration."""

    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "development-secret-key-change-me-123456"
    )
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", SECRET_KEY)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = False


class DevelopmentConfig(Config):
    """Define development configuration."""

    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DEV_DATABASE_URL",
        "sqlite:///development.db"
    )


class ProductionConfig(Config):
    """Define production configuration for MySQL."""

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "mysql+pymysql://hbnb:hbnb@localhost/hbnb"
    )


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig
}
