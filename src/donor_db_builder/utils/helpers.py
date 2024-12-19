import pandas as pd
import numpy as np
from uuid import uuid4
from pathlib import Path


def _generate_uuid(_):
    """Generate a UUID string for filer IDs"""
    return str(uuid4())


def get_data_dir() -> Path:
    return Path.cwd() / "data"
