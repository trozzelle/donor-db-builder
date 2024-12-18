from gqlalchemy import Memgraph, Node
from typing import Type, Dict, List, Any
import pandas as pd
from loguru import logger
from pathlib import Path
import uuid
from src.donor_db_builder.utils.logger import Logger
from models.Filer import Filer
from models.Contribution import Contribution
from models.Donor import Donor
import utils.cleaning as clean
from collections import ChainMap

logger = Logger.get_logger()

class DonorGraph:
    def __init__(self, host: str, port: int, username: str, password: str):
        # self.db = GraphDatabase.driver(uri, auth=(username, password))
        self.db = Memgraph(host=host, port=port, username=username, password=password)
        logger.info("Initializing DonorGraph")

    @logger.catch
    def clear_database(self):
        logger.debug("Deleting all nodes and relationships")
        self.db.execute("MATCH (n) DETACH DELETE n")
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
        set_clause = ", ".join([
            f"n.{name} = item.{name}"
            for name in fields.keys()
        ])
        
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
            properties: List[str]
    ) -> str:       
        """Generate query for creating relationships with nodes"""

        # Build property map for the node
        property_set = ", ".join([
            f"{prop}: item.{prop}"
            for prop in properties
        ])

        # Extract label and match conditions for start and end nodes

        start_label = next(iter(start_node_match.keys()))
        end_label = next(iter(end_node_match.keys()))

        # Build match conditions for start and end nodes
        start_match = ", ".join([
            f"{k}: item.{v}"
            for k, v in start_node_match[start_label].items()
        ])
        end_match = ", ".join([
            f"{k}: item.{v}"
            for k, v in end_node_match[end_label].items()
        ])

        return f"""
        UNWIND $items AS item
        MATCH (start:{start_label} {{{start_match}}})
        MATCH (end:{end_label} {{{end_match}}})
        CREATE (start)-[:{start_relationship_type}]->(node:{model.__name__} {{{property_set}}})-[:{end_relationship_type}]->(end)
        """


    @logger.catch
    def load_data(self, 
                 df: pd.DataFrame,
                 model: Type[Node],
                 field_mappings: Dict[str, str],
                 identifier_field: str,
                 transformers: Dict[str, callable] = None) -> None:
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

            # Generate and execute query
            query = self._generate_merge_query(model, identifier_field)
            self.db.execute(query, {'items': items})
            
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
            transformers: Dict[str, callable] = None
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
                list(field_mappings.keys())
            )

            self.db.execute(query, {'items': items})
            logger.success(f"Successfully loaded {len(items)} {model.__name__} records with relationships")

        except Exception as e:
            logger.error(f"Error loading {model.__name__} data with relationships: {str(e)}")
            raise



if __name__ == "__main__":


    contributions_df = pd.read_csv(Path.cwd()/'data'/'cf_data.csv', escapechar='\\')
    filers_df = pd.read_csv(Path.cwd()/'data'/'cf_filers.csv', escapechar='\\')

    uri = f"bolt://localhost:7687"
    username = ""
    password = ""

    # contributions_df['ID'] = contributions_df.apply(lambda _: str(uuid.uuid4()), axis=1)

    db = DonorGraph(host="localhost", port=7687, username="", password="")
    # db.clear_database()

    logger.info("Preparing donor data")
    contributions_df['donor_type'] = contributions_df['FLNG_ENT_FIRST_NAME'].apply(
        lambda x: 'Individual' if not pd.isna(x) else 'Organization'
    )

    contributions_df['donor_name'] = contributions_df.apply(
        lambda row: (f"{row['FLNG_ENT_FIRST_NAME']} {row['FLNG_ENT_LAST_NAME']}".strip()
                     if row['donor_type'] == 'Individual'
                     else clean.clean_name(row['FLNG_ENT_NAME'])),
        axis=1
    )

    contributions_df['donor_id'] = contributions_df.apply(
        clean.generate_donor_id, axis=1
    )

    # print('test')
    # # Load filers
    # filer_mappings = {
    #     'id': 'id',  # Will be generated
    #     'filer_id': 'FILER_ID',
    #     'name': 'FILER_NAME',
    #     'type': 'FILER_TYPE_DESC',
    #     'status': 'FILER_STATUS',
    #     'office': 'OFFICE_DESC',
    #     'district': 'DISTRICT',
    #     'county': 'COUNTY_DESC'
    # }
    #
    # filer_transformers = {
    #     'id': lambda _: str(uuid.uuid4())
    # }
    #
    # db.load_data(
    #     filers_df,
    #     Filer,
    #     filer_mappings,
    #     'id',
    #     filer_transformers
    # )
    #
    # # db.import_data(contributions_df, filers_df)
    #
    # # Load donors
    # donor_mappings = {
    #     'id': 'donor_id',
    #     'name': 'donor_name',
    #     'type': 'donor_type',
    #     'address': 'FLNG_ENT_ADD1',
    #     'city': 'FLNG_ENT_CITY',
    #     'state': 'FLNG_ENT_STATE',
    #     'zip': 'FLNG_ENT_ZIP'
    # }
    #
    # db.load_data(
    #     contributions_df,
    #     Donor,
    #     donor_mappings,
    #     'id'
    # )
    #
    # # Load contributions with relationships
    # contribution_mappings = {
    #     'transaction_id': 'TRANS_NUMBER',
    #     'amount': 'ORG_AMT',
    #     'date': 'SCHED_DATE',
    #     'payment_type': 'PAYMENT_TYPE_DESC',
    #     'contributor_type': 'CNTRBR_TYPE_DESC',
    #     'payment_method': 'PAYMENT_TYPE_DESC'
    # }
    #
    # contribution_transformers = {
    #     # 'amount': float,
    #     # 'date': lambda x: f"datetime('{x}')"
    # }
    # #
    # # db.load_data_with_relationships(
    # #     contributions_df,
    # #     Contribution,
    # #     contribution_mappings,
    # #     start_node_match={'id': 'donor_id'},
    # #     end_node_match={'filer_id': 'FILER_ID'},
    # #     start_relationship_type='MADE',
    # #     end_relationship_type='TO',
    # #     transformers=contribution_transformers
    # # )
    #
    # db.load_data_with_relationships(
    #     contributions_df,
    #     Contribution,
    #     contribution_mappings,
    #     start_node_match={'Donor': {'id': 'donor_id'}},
    #     end_node_match={'Filer': {'filer_id': 'FILER_ID'}},
    #     start_relationship_type='MADE',
    #     end_relationship_type='TO',
    #     transformers=contribution_transformers
    # )