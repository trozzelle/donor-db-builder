from gqlalchemy import Memgraph, Node, Field, Relationship
from typing import Optional
import pandas as pd
import uuid

db = Memgraph()


class Filer(Node):
    """
    Represents a candidate or committee registered with the NY BOE
    """

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()), unique=True, db=Memgraph()
    )
    filer_id: str = Field(db=Memgraph())
    name: str
    type: str
    compliance_type: str
    committee_type: str
    status: str
    office: Optional[str]
    district: Optional[str]
    county: Optional[str]
    municipality: Optional[str]
    subdivision: Optional[str]

    @classmethod
    def bulk_save(cls, filers_df: pd.DataFrame, db: Memgraph):
        """Bulk save filers using UNWIND"""
        filers = [
            {
                "id": str(uuid.uuid4()),
                "filer_id": row["FILER_ID"],
                "name": row["FILER_NAME"],
                "type": row["FILER_TYPE_DESC"],
                "compliance_type": row["COMPLIANCE_TYPE_DESC"],
                "committee_type": row["COMMITTEE_TYPE_DESC"],
                "status": row["FILER_STATUS"],
                "office": row["OFFICE_DESC"],
                "district": row["DISTRICT"],
                "county": row["COUNTY_DESC"],
                # 'municipality': row['MUNICIPALITY'],
                # 'subdivision': row['SUBDIVISION'],
            }
            for _, row in filers_df.iterrows()
        ]

        query = """
        UNWIND $filers AS filer
        MERGE (f:Filer {id: filer.id})
        SET f += {
            filer_id: filer.filer_id,
            name: filer.name,
            type: filer.type,
            compliance_type: filer.compliance_type,
            committee_type: filer.committee_type,
            status: filer.status,
            office: filer.office,
            district: filer.district,
            county: filer.county,
            municipality: filer.municipality,
            subdivision: filer.subdivision
        }
        """
        db.execute(query, {"filers": filers})


class Registered_At(Relationship, type="REGISTERED_AT"):
    """
    Represents a relationship between a filer and a location where they are registered
    """

    pass
