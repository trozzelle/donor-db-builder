from donor_db_builder.database.gqlalchemy.graph_importer import GraphImporter
from typing import Dict, Any
import pandas as pd


def process_nodes(chunk: pd.DataFrame, db_config: Dict[str, Any], **kwargs) -> None:
    """
    Process a chunk of nodes.

    Args:
        chunk: DataFrame chunk to process
        db_config: Database configuration
        kwargs: Additional arguments including model, field_mappings, etc.
    """
    # Create a new GraphImporter instance for this chunk
    db = GraphImporter(
        host=db_config["host"],
        port=db_config["port"],
        username=db_config["username"],
        password=db_config["password"],
    )

    try:
        db.load_data(
            df=chunk,
            model=kwargs["model"],
            field_mappings=kwargs["field_mappings"],
            identifier_field=kwargs["identifier_field"],
            transformers=kwargs.get("transformers"),
        )
    finally:
        del db


def process_relationships(
    chunk: pd.DataFrame, db_config: Dict[str, Any], **kwargs
) -> None:
    """
    Process a chunk of relationships.

    Args:
        chunk: DataFrame chunk to process
        db_config: Database configuration
        kwargs: Additional arguments including model, field_mappings, etc.
    """
    # Create a new GraphImporter instance for this chunk
    db = GraphImporter(
        host=db_config["host"],
        port=db_config["port"],
        username=db_config["username"],
        password=db_config["password"],
    )

    try:
        db.load_data_with_relationships(
            df=chunk,
            model=kwargs["model"],
            field_mappings=kwargs["field_mappings"],
            start_node_match=kwargs["start_node_match"],
            end_node_match=kwargs["end_node_match"],
            start_relationship_type=kwargs["start_relationship_type"],
            end_relationship_type=kwargs["end_relationship_type"],
            transformers=kwargs.get("transformers"),
        )
    finally:
        del db
