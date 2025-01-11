from typing import ClassVar, Optional, List
from sqlmodel import Field
from datetime import datetime


class IndividualBase:
    first_name: str | None = Field(description="First name of the donor")
    last_name: str | None = Field(description="Last name of the donor")


class OrganizationBase:
    name: str | None = Field(description="Name of the organization")
    location_id: int | None = Field(description="Foreign key to the location table")


class LocationBase:
    street_address: str = Field(description="Street address of the location")
    city: str = Field(description="City of the location")
    state: str = Field(description="State of the location")
    zip_code: str = Field(description="Zip code of the location")
    country: str = Field(description="Country of the location")


class PaymentBase:
    amount: float | None = Field(description="Amount of the payment")
    type: str | None = Field(description="Type of the payment")
    date: datetime | None = Field(description="Date of the payment")
    transaction_id: str | None = Field(description="Transaction ID of the payment")
    filer_id: int | None = Field(description="Filer ID of the payment")
    payer_type: str | None = Field(
        description="Payer type of the payment", nullable=False
    )
    payer_id: int = Field(description="Payer ID of the payment", nullable=False)


class FilerBase:
    filer_id: int | None = Field(description="")
    filer_name: str | None = Field(description="")
    compliance_type: str | None = Field(description="")
    filer_type: str | None = Field(description="")
    office: str | None = Field(description="")
    district: str | None = Field(description="")
    county: str | None = Field(description="")
