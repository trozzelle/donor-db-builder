from typing import ClassVar, Optional, List
from neontology import BaseNode, BaseRelationship, init_neontology

from .BaseModels import (
    IndividualBase,
    OrganizationBase,
    LocationBase,
    FilerBase,
    PaymentBase,
)


class Individual(IndividualBase, BaseNode):
    __primarylabel__: ClassVar = "Individual"
    __primaryproperty__: ClassVar = "id"


class Organization(OrganizationBase, BaseNode):
    __primarylabel__: ClassVar = "Organization"
    __primaryproperty__: ClassVar = "id"


class Location(LocationBase, BaseNode):
    __primarylabel__: ClassVar = "Location"
    __primaryproperty__: ClassVar = "id"


class Filer(FilerBase, BaseNode):
    __primarylabel__: ClassVar = "Filer"
    __primaryproperty__: ClassVar = "id"


class Payment(PaymentBase, BaseNode):
    __primarylabel__: ClassVar = "Payment"
    __primaryproperty__: ClassVar = "id"


class DonatedIndRel(BaseRelationship):
    __relationshiptype__: ClassVar = "DONATED"

    source: Individual
    target: Payment


class DonatedOrgRel(BaseRelationship):
    __relationshiptype__: ClassVar = "DONATED"

    source: Organization
    target: Payment


class ReceivedRel(BaseRelationship):
    __relationshiptype__: ClassVar = "RECEIVED"

    source: Payment
    target: Filer


class LocatedIndRel(BaseRelationship):
    __relationshiptype__: ClassVar = "LOCATED"

    source: Individual
    target: Location


class LocatedOrgRel(BaseRelationship):
    __relationshiptype__: ClassVar = "LOCATED"

    source: Organization
    target: Location


class LocatedFilerRel(BaseRelationship):
    __relationshiptype__: ClassVar = "LOCATED"

    source: Filer
    target: Location
