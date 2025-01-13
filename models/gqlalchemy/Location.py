from gqlalchemy import Node, Relationship, Field, Memgraph
import pandas as pd


class Location(Node):
    """
    Represents a physical location.
    """

    id: str = Field(db=Memgraph())
    address: str
    city: str
    state: str
    zip: str
    latitude: float
    longitude: float


class Located_At(Relationship, type="LOCATED_AT"):
    """
    Represents a relationship between an entity and a location.
    """

    pass
