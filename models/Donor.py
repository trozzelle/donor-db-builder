from gqlalchemy import Node, Field, Memgraph
import pandas as pd

class Donor(Node):
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