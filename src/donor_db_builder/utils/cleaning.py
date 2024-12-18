import hashlib
import pandas as pd
import re

def generate_donor_id(row: pd.Series) -> str:
    """Generate unique ID for donor by hashing their attributes"""
    if pd.isna(row['FLNG_ENT_FIRST_NAME']):
        key_parts = [
            str(row['FLNG_ENT_NAME']).upper(),
            str(row['FLNG_ENT_ADD1']).upper(),
            str(row['FLNG_ENT_ZIP'])[:5]
        ]
    else:
        key_parts = [
            str(row['FLNG_ENT_FIRST_NAME']).upper(),
            str(row['FLNG_ENT_LAST_NAME']).upper(),
            str(row['FLNG_ENT_ADD1']).upper(),
            str(row['FLNG_ENT_ZIP'])[:5]
        ]

    key = '|'.join(filter(None, key_parts))
    return hashlib.md5(key.encode()).hexdigest()

def clean_name(name: str) -> str:

    if pd.isna(name):
        return ""

    name = re.sub(r'\s+(Inc\.?|LLC|Corp\.?|LLP)$', '', name, flags=re.IGNORECASE)

    return name.strip()