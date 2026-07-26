#!/usr/bin/python3
"""Define configuration classes for the HBnB application."""

import os


class Config:
    """Define common application configuration."""

    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "default-secret-key"
    )
    DEBUG = False


class DevelopmentConfig(Config):
    """Define development configuration."""

    DEBUG = True


config = {
    "development": DevelopmentConfig,
    "default": DevelopmentConfig
}
