from typing import ClassVar, Optional, List
from sqlmodel import Field, SQLModel, Relationship, Integer, Sequence, Column
from .helpers import generate_id_sequence
from datetime import datetime
from .BaseModels import (
    IndividualBase,
    OrganizationBase,
    LocationBase,
    PaymentBase,
    FilerBase,
)


# def id_field(table_name: str):
#     sequence = Sequence(f"{table_name}_sequence", metadata=SQLModel.metadata)
#     return Field(
#         default=None,
#         primary_key=True,
#         sa_column_args=[sequence],
#         sa_column_kwargs={"server_default": sequence.next_value()},
#     )


class Individual(SQLModel, IndividualBase, table=True):
    # id: int | None = Field(
    #     default_factory=generate_id_sequence("individual"),
    #     primary_key=True,
    #     description="",
    # )

    individual_id_seq: ClassVar = Sequence("individual_id_seq")
    id: int | None = Field(
        default=None,
        primary_key=True,
        sa_column_args=[individual_id_seq],
        sa_column_kwargs={"server_default": individual_id_seq.next_value()},
    )

    # id: int | None = id_field("individual")

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
    # id: int | None = Field(
    #     default_factory=generate_id_sequence("organization"),
    #     primary_key=True,
    #     description="",
    organization_id_seq: ClassVar = Sequence("organization_id_seq")
    id: int | None = Field(
        default=None,
        primary_key=True,
        sa_column_args=[organization_id_seq],
        sa_column_kwargs={"server_default": organization_id_seq.next_value()},
    )

    # id: int | None = id_field("organization")

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
    # id: int | None = Field(
    #     default_factory=generate_id_sequence("location"),
    #     primary_key=True,
    #     description="",
    # )
    location_id_seq: ClassVar = Sequence("location_id_seq")
    id: int | None = Field(
        default=None,
        primary_key=True,
        sa_column_args=[location_id_seq],
        sa_column_kwargs={"server_default": location_id_seq.next_value()},
    )
    # id: int | None = id_field("location")

    individuals: List["Individual"] = Relationship(back_populates="location")
    organizations: List["Organization"] = Relationship(back_populates="location")
    filers: List["Filer"] = Relationship(back_populates="location")


class Payment(SQLModel, PaymentBase, table=True):
    # id: int | None = Field(
    #     default_factory=generate_id_sequence("payment"),
    #     primary_key=True,
    #     description="",
    # )
    payment_id_seq: ClassVar = Sequence("payment_id_seq")
    id: int | None = Field(
        default=None,
        primary_key=True,
        sa_column_args=[payment_id_seq],
        sa_column_kwargs={"server_default": payment_id_seq.next_value()},
    )

    # id: int | None = id_field("payment")

    filer_id: int | None = Field(
        foreign_key="filer.id", description="Foreign key to the filer table"
    )

    filer: "Filer" = Relationship(back_populates="payments")
    # individual: Individual = Relationship(
    #     sa_relationship_kwargs={
    #         "foreign_keys": "[Individual.id]",
    #         "primaryjoin": "and_(Payment.payer_id==Individual.id, "
    #         "Payment.payer_type=='individual')",
    #     }
    # )
    # individual: Optional[Individual] = Relationship(
    #     back_populates="payments",
    #     sa_relationship_kwargs={
    #         "foreign_keys": "[Individual.id]",
    #         "primaryjoin": "and_(Payment.payer_id==foreign(Individual.id), "
    #         "Payment.payer_type=='individual')",
    #     },
    # )
    # organization: Optional[Organization] = Relationship(
    #     back_populates="payments",
    #     sa_relationship_kwargs={
    #         "foreign_keys": "[Organization.id]",
    #         "primaryjoin": "and_(Payment.payer_id==foreign(Organization.id), "
    #         "Payment.payer_type=='organization')",
    #     },
    # )
    individual: Optional[Individual] = Relationship(
        back_populates="payments",
        sa_relationship_kwargs={
            # "foreign_keys": "[Individual.id]",
            "primaryjoin": "and_(foreign(Payment.payer_id)==Individual.id, "
            "Payment.payer_type=='individual')",
        },
    )
    organization: Optional[Organization] = Relationship(
        back_populates="payments",
        sa_relationship_kwargs={
            # "foreign_keys": "[Organization.id]",
            "primaryjoin": "and_(foreign(Payment.payer_id)==Organization.id, "
            "Payment.payer_type=='organization')",
        },
    )


class Filer(SQLModel, FilerBase, table=True):
    # id: int | None = Field(
    #     default_factory=generate_id_sequence("filer"),
    #     primary_key=True,
    #     description="",
    # )
    filer_id_seq: ClassVar = Sequence("filer_id_seq")
    id: int | None = Field(
        default=None,
        primary_key=True,
        sa_column_args=[filer_id_seq],
        sa_column_kwargs={"server_default": filer_id_seq.next_value()},
    )

    # id: int | None = id_field("filer")

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
