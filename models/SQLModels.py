from typing import ClassVar, Optional, List
from sqlmodel import Field, SQLModel, Relationship
from .helpers import generate_id_sequence
from datetime import datetime
from .BaseModels import (
    IndividualBase,
    OrganizationBase,
    LocationBase,
    PaymentBase,
    FilerBase,
)


class Individual(SQLModel, IndividualBase, table=True):
    id: int | None = Field(
        default_factory=generate_id_sequence("individual"),
        primary_key=True,
        description="",
    )

    location_id: int | None = Field(
        default=None,
        foreign_key="location.id",
        description="Foreign key to the location table",
    )

    location: "Location" = Relationship(back_populates="individuals")
    payments: List["Payment"] = Relationship(
        back_populates="individual",
        sa_relationship_kwargs={
            "primaryjoin": "and_(Payment.payer_id==Individual.id, "
            "Payment.payer_type=='individual')"
        },
    )


class Organization(SQLModel, OrganizationBase, table=True):
    id: int | None = Field(
        default_factory=generate_id_sequence("organization"),
        primary_key=True,
        description="",
    )

    location_id: int | None = Field(
        default=None,
        foreign_key="location.id",
        description="Foreign key to the location table",
    )

    location: "Location" = Relationship(back_populates="organization")
    payments: List["Payment"] = Relationship(
        back_populates="organization",
        sa_relationship_kwargs={
            "primaryjoin": "and_(Payment.payer_id==Organization.id, "
            "Payment.payer_type=='organization')"
        },
    )


class Location(SQLModel, LocationBase, table=True):
    id: int | None = Field(
        default_factory=generate_id_sequence("location"),
        primary_key=True,
        description="",
    )

    individuals: List["Individual"] = Relationship(back_populates="location")
    organizations: List["Organization"] = Relationship(back_populates="location")
    filers: List["Filer"] = Relationship(back_populates="location")


class Payment(SQLModel, PaymentBase, table=True):
    id: int | None = Field(
        default_factory=generate_id_sequence("payment"),
        primary_key=True,
        description="",
    )

    filer_id: int | None = Field(
        foreign_key="filer.id", description="Foreign key to the filer table"
    )

    filer: "Filer" = Relationship(back_populates="payments")
    individual: Individual = Relationship(
        sa_relationship_kwargs={
            "foreign_keys": "[Payment.payer_id]",
            "primaryjoin": "and_(Payment.payer_id==Individual.id, "
            "Payment.payer_type=='individual')",
        }
    )
    organization: Organization = Relationship(
        sa_relationship_kwargs={
            "foreign_keys": "[Payment.payer_id]",
            "primaryjoin": "and_(Payment.payer_id==Organization.id, "
            "Payment.payer_type=='organization')",
        }
    )


class Filer(SQLModel, FilerBase, table=True):
    id: int | None = Field(
        default_factory=generate_id_sequence("filer"),
        primary_key=True,
        description="",
    )

    location_id: int = Field(
        foreign_key="location.id", description="Foreign key to the location table"
    )

    location: Location = Relationship(back_populates="filers")
    payments: List["Payment"] = Relationship(back_populates="filer")


class Config:
    table_args = {
        "check_constraints": [
            "payer_type IN ('individual', 'organization')",
        ]
    }
