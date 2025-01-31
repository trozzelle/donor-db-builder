from donor_db_builder.app import RaisingApp
from donor_db_builder.settings import settings


def run() -> None:
    """Run the Raising app"""
    print(f"Settings folder {settings.settings_dir}")
    RaisingApp().run()


if __name__ == "__main__":
    run()
