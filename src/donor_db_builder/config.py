import os
import json
import click
from pathlib import Path
from dotenv import dotenv_values
from tomlkit.toml_document import TOMLDocument
from tomlkit.toml_file import TOMLFile
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional, Any

CONFIG_DIR = Path(__file__).resolve().parent / "config"
# CONFIG_FILE = "config.json"
ENV_FILE = CONFIG_DIR / ".env"

config_labels = {
    "DB_HOST": {
        "label": "DB Host",
        "description": "The host of the database",
        "placeholder": "localhost",
    },
    "DB_PORT": {
        "label": "DB Port",
        "description": "The port of the database",
        "placeholder": "5432",
    },
    "DB_USER": {
        "label": "DB User",
        "description": "The user of the database",
        "placeholder": "postgres",
    },
    "DB_PASS": {
        "label": "DB Password",
        "description": "The password of the database",
        "placeholder": "****",
    },
    "SOCRATA_API_KEY": {
        "label": "Socrata Key",
        "description": "The API key for the Socrata API",
        "placeholder": "****",
    },
}


class Config(BaseSettings):
    DB_HOST: str = Field(default="localhost", description="The host of the database")
    DB_PORT: int = Field(default=5432, description="The port of the database")
    DB_USER: str = Field(default="postgres", description="The user of the database")
    DB_PASS: str = Field(
        default="<PASSWORD>", description="The password of the database"
    )
    SOCRATA_API_KEY: Optional[str] = Field(
        default=None, description="The API key for the Socrata API"
    )

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # DB_NAME: str = "donor_atlas"
    # DB_SCHEMA: str = "public"
    # DB_DRIVER: str = "psycopg2"
    # DB_URL: str = Field(
    #     None,
    # )


class Settings:
    def __init__(self):
        self.config = Config()
        self.labels = config_labels

    def save_to_env(self) -> None:
        """Save configuration to .env file"""
        env_content = []
        for field, value in self.config.model_dump().items():
            env_content.append(f"{field}={value}")
        with open(ENV_FILE, "w") as f:
            f.write("\n".join(env_content))

    def get(self, field_name: str) -> Any:
        """Get a setting from config"""
        if not hasattr(self.config, field_name):
            raise ValueError(f"Field {field_name} not found in config")
        return getattr(self.config, field_name)

    def set(self, field_name: str, value: Any) -> None:
        """Set a setting in config"""
        if not hasattr(self.config, field_name):
            raise ValueError(f"Field {field_name} not found in config")
        setattr(self.config, field_name, value)
        self.save_to_env()

    def get_all(self):
        return self.config.model_dump()

    def get_all_with_labels(self):
        return (self.config.model_dump(), self.labels)

    def load_from_env(self) -> None:
        """Load configuration from .env file"""
        env_vars = dotenv_values(ENV_FILE)
        for field, value in env_vars.items():
            self.set(field, value)

    def update_from_dict(self, config_dict: dict) -> None:
        """Update configuration from a dictionary"""

        validated_config = self.config.model_validate(config_dict)

        for field, value in config_dict.items():
            self.set(field, value)
        self.save_to_env()


# class Config(object):
#     """
#     Class that handles loading and saving configuration to file
#     """
#
#     def __init__(self):
#         self.config = self.load()
#
#     def load(self):
#         """Load configuration from file"""
#         if not os.path.exists(CONFIG_DIR):
#             return {}
#
#         try:
#             with open(CONFIG_DIR / CONFIG_FILE, "r") as f:
#                 return json.load(f)
#         except Exception as e:
#             click.echo(f"Error loading config: {e}", err=True)
#             return {}
#
#     def save(self):
#         """Save configuration to file"""
#         if not os.path.exists(CONFIG_DIR):
#             os.makedirs(CONFIG_DIR)
#
#         try:
#             with open(CONFIG_DIR / CONFIG_FILE, "w") as f:
#                 json.dump(self.config, f, indent=2)
#         except Exception as e:
#             click.echo(f"Error saving config: {e}", err=True)
#
#     def get(self, key, default=None):
#         """Get a setting from config"""
#         return self.config.get(key, default)
#
#     def set(self, key, value):
#         """Set a setting in config"""
#         self.config[key] = value


if __name__ == "__main__":
    settings = Settings()
    settings.save_to_env()
