import os
import json
import click

# CONFIG_DIR = click.get_app_dir("donor-db-builder")
CONFIG_DIR = os.getcwd() + "/.config"
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")


def load_config():
    """Load configuration from file"""
    if not os.path.exists(CONFIG_FILE):
        return {}

    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        click.echo(f"Error loading config: {e}", err=True)
        return {}


def save_config(config):
    """Save configuration to file"""
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)

    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        click.echo(f"Error saving config: {e}", err=True)


def get_setting(key, default=None):
    """Get a setting from config"""
    config = load_config()
    return config.get(key, default)


def set_setting(key, value):
    """Set a setting in config"""
    config = load_config()
    config[key] = value
    save_config(config)