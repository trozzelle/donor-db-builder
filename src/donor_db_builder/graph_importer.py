from typing import Dict, List, Type

import pandas as pd
from gqlalchemy import Node
from loguru import logger
from neo4j import GraphDatabase

from src.donor_db_builder.utils.logger import Logger

logger = Logger.get_logger()


class GraphImporter:
    """
    A generic class for importing data into a Neo4j graph database
    with queries generated from GQLAlchemy models.
    """

    def __init__(self, host: str, port: int, username: str, password: str):
        # self.db = GraphDatabase.driver(uri, auth=(username, password))
        # self.db = Memgraph(host=host, port=port, username=username, password=password)
        uri = f"bolt://localhost:7687"
        self.db = GraphDatabase.driver(uri, auth=("tr", "memgraph"))

        logger.info("Initializing GraphImporter")

    @logger.catch
    def clear_database(self):
        """
        Truncates all nodes and relationships in the database.
        """
        logger.debug("Deleting all nodes and relationships")
        self.db.execute_query("MATCH (n) DETACH DELETE n")
        logger.info("Database cleared successfully")

    def _generate_merge_query(self, model: Type[Node], identifier_field: str) -> str:
        """Generate MERGE query from model class"""
        # Get all fields from model
        fields = {
            name: field
            for name, field in model.__annotations__.items()
            if name != identifier_field
        }

        # Build SET clause
        set_clause = ", ".join([f"n.{name} = item.{name}" for name in fields.keys()])

        return f"""
        UNWIND $items AS item
        MERGE (n:{model.__name__} {{{identifier_field}: item.{identifier_field}}})
        SET {set_clause}
        """

    def _generate_relationships_query(
        self,
        model: Type[Node],
        start_node_match: Dict[str, Dict[str, str]],
        end_node_match: Dict[str, Dict[str, str]],
        start_relationship_type: str,
        end_relationship_type: str,
        properties: List[str],
    ) -> str:
        """Generate query for creating relationships with nodes"""

        # Build property map for the node
        property_set = ", ".join([f"{prop}: item.{prop}" for prop in properties])

        # Extract label and match conditions for start and end nodes

        start_label = next(iter(start_node_match.keys()))
        end_label = next(iter(end_node_match.keys()))

        # Build match conditions for start and end nodes
        start_match = ", ".join(
            [f"{k}: item.{v}" for k, v in start_node_match[start_label].items()]
        )
        end_match = ", ".join(
            [f"{k}: item.{v}" for k, v in end_node_match[end_label].items()]
        )

        return f"""
        UNWIND $items AS item
        MATCH (start:{start_label} {{{start_match}}})
        MATCH (end:{end_label} {{{end_match}}})
        CREATE (start)-[:{start_relationship_type}]->(node:{model.__name__} {{{property_set}}})-[:{end_relationship_type}]->(end)
        """

    @logger.catch
    def load_data(
        self,
        df: pd.DataFrame,
        model: Type[Node],
        field_mappings: Dict[str, str],
        identifier_field: str,
        transformers: Dict[str, callable] = None,
    ) -> None:
        """
        Load data from DataFrame into graph using model definition

        Args:
            df: Source DataFrame
            model: GQLAlchemy Node model class
            field_mappings: Dict mapping model fields to DataFrame columns
            identifier_field: Field to use for MERGE matching
            transformers: Optional dict of field transformation functions
        """
        logger.info(f"Loading {len(df)} records into {model.__name__}")

        try:
            # Transform data according to mappings
            items = []
            for _, row in df.iterrows():
                item = {}
                for model_field, df_field in field_mappings.items():
                    value = None
                    # Apply transformer if one exists
                    if transformers and model_field in transformers:
                        value = transformers[model_field](value)
                    else:
                        value = row[df_field]

                    item[model_field] = value
                items.append(item)

            # Generate and execute_query query
            query = self._generate_merge_query(model, identifier_field)
            self.db.execute_query(
                query, parameters_={"items": items}, database_="memgraph"
            )

            logger.success(f"Successfully loaded {len(items)} {model.__name__} records")

        except Exception as e:
            logger.error(f"Error loading {model.__name__} data: {str(e)}")
            raise

    @logger.catch
    def load_data_with_relationships(
        self,
        df: pd.DataFrame,
        model: Type[Node],
        field_mappings: Dict[str, str],
        start_node_match: Dict[str, Dict[str, str]],
        end_node_match: Dict[str, Dict[str, str]],
        start_relationship_type: str,
        end_relationship_type: str,
        transformers: Dict[str, callable] = None,
    ) -> None:
        """
        Load data and create relationships

        Args:
            df: Source DataFrame
            model: Node model class
            field_mappings: Dict mapping model fields to DataFrame columns
            start_node_match: Dict of fields to match start node
            end_node_match: Dict of fields to match end node
            relationship_type: Type of relationship to create
            transformers: Optional dict of field transformation functions
        """
        logger.info(f"Loading {len(df)} {model.__name__} records with relationships")

        try:
            items = []
            for _, row in df.iterrows():
                item = {}
                # Map fields for the node
                for model_field, df_field in field_mappings.items():
                    value = None
                    # Apply transformer if one exists
                    if transformers and model_field in transformers:
                        value = transformers[model_field](value)
                    else:
                        value = row[df_field]
                    item[model_field] = value

                # Add fields needed for relationship matching
                for match_dict in [start_node_match, end_node_match]:
                    label = next(iter(match_dict.keys()))
                    for _, df_field in match_dict[label].items():
                        item[df_field] = row[df_field]

                items.append(item)

            query = self._generate_relationships_query(
                model,
                start_node_match,
                end_node_match,
                start_relationship_type,
                end_relationship_type,
                list(field_mappings.keys()),
            )

            self.db.execute_query(
                query, parameters_={"items": items}, database_="memgraph"
            )
            logger.success(
                f"Successfully loaded {len(items)} {model.__name__} records with relationships"
            )

        except Exception as e:
            logger.error(
                f"Error loading {model.__name__} data with relationships: {str(e)}"
            )
            raise
