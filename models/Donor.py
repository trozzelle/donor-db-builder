from gqlalchemy import Node, Field, Memgraph
import pandas as pd

class Donor(Node):
    """
    Represents a donor of campaign contributions
    """
    id: str = Field(unique=True, db=Memgraph())
    name: str
    type: str  # 'Individual' or 'Organization'
    address: str
    city: str
    state: str
    zip: str

    @classmethod
    def bulk_save(cls, donors_df: pd.DataFrame, db: Memgraph):
        """Bulk save donors using UNWIND"""
        donors = [
            {
                'id': row['donor_id'],
                'name': row['donor_name'],
                'type': row['donor_type'],
                'address': row['FLNG_ENT_ADD1'],
                'city': row['FLNG_ENT_CITY'],
                'state': row['FLNG_ENT_STATE'],
                'zip': row['FLNG_ENT_ZIP']
            }
            for _, row in donors_df.iterrows()
        ]

        query = """
        UNWIND $donors AS donor
        MERGE (d:Donor {id: donor.id})
        SET d += {
            name: donor.name,
            type: donor.type,
            address: donor.address,
            city: donor.city,
            state: donor.state,
            zip: donor.zip
        }
        """
        db.execute(query, {'donors': donors})

"""
One-off functions to clean up the data for this model
"""

def _set_type(x):
    """
    Set the type of the donor based on the donor_type column

    Args:
        x (str): The donor_type column from the donors dataframe

    Returns:
        str: Donor entity type
    """
    return "Individual" if not pd.isna(x) else "Organization"


def _donor_name(row):
    """
    Set the name of the donor based on the donor_type column

    Args:
        row (pd.Series): A row from the donors dataframe

    Returns:
        str: The full name of the individual donor, or the name of the organization
    """
    return (
        f"{row['FLNG_ENT_FIRST_NAME']} {row['FLNG_ENT_LAST_NAME']}".strip()
        if row["donor_type"] == "Individual"
        else clean_name(row["FLNG_ENT_NAME"])
    )