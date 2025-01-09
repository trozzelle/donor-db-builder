from typing import Dict, Any
from neo4j import GraphDatabase, Driver
from loguru import logger


class GraphEnricher:
    """Updates graph database with extracted information"""

    def __init__(self, driver: Driver):
        self.driver = driver

    def enrich_donor(self, donor_id: str, extracted_data: Dict[str, Any]):
        """Adds extracted information to donor node"""

        with self.driver.session() as session:
            for entity in extracted_data.get("entities", []):
                # TODO: Change to GQLAlchemy
                session.run(
                    """
                MATCH (d:Donor {id: $donor_id}
                MERGE (e:Entity {
                    text: $text,
                    type: $type,})
                MERGE (d)-[:MENTIONED]->(e)
                """,
                    {
                        "donor_id": donor_id,
                        "text": entity.get("text"),
                        "type": entity.get("type"),
                    },
                )
