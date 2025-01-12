from typing import ClassVar, Optional, List
from sqlmodel import Field, SQLModel, Relationship, Sequence
from .BaseModels import (
    IndividualBase,
    OrganizationBase,
    LocationBase,
    PaymentBase,
    FilerBase,
)

"""
Models for the SQLAlchemy classes that represent the db schema.

Sequences currently need to be created manually in the schema for 
reasons I have not yet debugged.

ID columns are currently not created first in the table schema. This
is because SQLModel executes the Field() (Column()) call before the 
sa_column_args. Leaving as-is for now because it should be obviated
by building a more dynamic schema generator.

https://github.com/fastapi/sqlmodel/issues/542
"""


class Individual(SQLModel, IndividualBase, table=True):
    individual_id_seq: ClassVar = Sequence("individual_id_seq")
    id: int | None = Field(
        default=None,
        primary_key=True,
        sa_column_args=[individual_id_seq],
        sa_column_kwargs={"server_default": individual_id_seq.next_value()},
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
            "foreign_keys": "[Payment.id]",
            "primaryjoin": "and_(foreign(Payment.payer_id)==Individual.id, "
            "foreign(Payment.payer_type)=='individual')",
        },
    )


class Organization(SQLModel, OrganizationBase, table=True):
    organization_id_seq: ClassVar = Sequence("organization_id_seq")
    id: int | None = Field(
        default=None,
        primary_key=True,
        sa_column_args=[organization_id_seq],
        sa_column_kwargs={"server_default": organization_id_seq.next_value()},
    )

    location_id: int | None = Field(
        default=None,
        foreign_key="location.id",
        description="Foreign key to the location table",
    )

    location: "Location" = Relationship(back_populates="organizations")
    payments: List["Payment"] = Relationship(
        back_populates="organization",
        sa_relationship_kwargs={
            "foreign_keys": "[Payment.id]",
            "primaryjoin": "and_(foreign(Payment.payer_id)==Organization.id, "
            "foreign(Payment.payer_type)=='organization')",
        },
    )


class Location(SQLModel, LocationBase, table=True):
    location_id_seq: ClassVar = Sequence("location_id_seq")
    id: int | None = Field(
        default=None,
        primary_key=True,
        sa_column_args=[location_id_seq],
        sa_column_kwargs={"server_default": location_id_seq.next_value()},
    )

    individuals: List["Individual"] = Relationship(back_populates="location")
    organizations: List["Organization"] = Relationship(back_populates="location")
    filers: List["Filer"] = Relationship(back_populates="location")


class Payment(SQLModel, PaymentBase, table=True):
    payment_id_seq: ClassVar = Sequence("payment_id_seq")
    id: int | None = Field(
        default=None,
        primary_key=True,
        sa_column_args=[payment_id_seq],
        sa_column_kwargs={"server_default": payment_id_seq.next_value()},
    )

    filer_id: int | None = Field(
        foreign_key="filer.id", description="Foreign key to the filer table"
    )
    filer: "Filer" = Relationship(back_populates="payments")

    # Even though this is a required foreign key, we need to
    # make it nullable since the field is populated after insert
    payer_id: int | None = Field(
        default=None, description="Foreign key to payer in Individual or Organization"
    )

    payer_type: str = Field(
        description="Type of the payer",
        nullable=False,
    )

    individual: Optional[Individual] = Relationship(
        back_populates="payments",
        sa_relationship_kwargs={
            "primaryjoin": "and_(foreign(Payment.payer_id)==Individual.id, "
            "Payment.payer_type=='individual')",
        },
    )
    organization: Optional[Organization] = Relationship(
        back_populates="payments",
        sa_relationship_kwargs={
            "primaryjoin": "and_(foreign(Payment.payer_id)==Organization.id, "
            "Payment.payer_type=='organization')",
        },
    )


class Filer(SQLModel, FilerBase, table=True):
    filer_id_seq: ClassVar = Sequence("filer_id_seq")
    id: int | None = Field(
        default=None,
        primary_key=True,
        sa_column_args=[filer_id_seq],
        sa_column_kwargs={"server_default": filer_id_seq.next_value()},
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
