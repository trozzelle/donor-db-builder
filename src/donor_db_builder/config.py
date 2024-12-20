import os
import json
import click

# CONFIG_DIR = click.get_app_dir("donor-db-builder")
CONFIG_DIR = os.getcwd() + "/.config"
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")


class Config(object):

    def __init__(self):
        self.config = self.load_config()

    def load_config(self):
        """Load configuration from file"""
        if not os.path.exists(CONFIG_FILE):
            return {}

        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            click.echo(f"Error loading config: {e}", err=True)
            return {}


    def save_config(self, config):
        """Save configuration to file"""
        if not os.path.exists(CONFIG_DIR):
            os.makedirs(CONFIG_DIR)

        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            click.echo(f"Error saving config: {e}", err=True)


    def get_setting(self, key, default=None):
        """Get a setting from config"""
        config = self.load_config()
        return config.get(key, default)


    def set_setting(self, key, value):
        """Set a setting in config"""
        config = self.load_config()
        config[key] = value
        self.save_config(config)
