from typing import ClassVar, Optional, List
from neontology import BaseNode, BaseRelationship, init_neontology

from models.SQLModels import PaymentBase, FilerBase


class IndividualGraphModel(IndividualBase, BaseNode):
    pass


class OrganizationGraphModel(OrganizationBase, BaseNode):
    pass


class LocationGraphModel(LocationBase, BaseNode):
    pass


class PaymentGraphModel(PaymentBase, BaseNode):
    pass


class FilerGraphModel(FilerBase, BaseNode):
    pass
