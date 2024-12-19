from neomodel import (
    config,
    db,
    StructuredNode,
    StringProperty,
    IntegerProperty,
    UniqueProperty,
    UniqueIdProperty,
    RelationshipTo,
)

config.DATABASE_URL = "bolt://tr:memgraph@localhost:7687"


class Country(StructuredNode):
    code = StringProperty(unique_index=True, required=True)


class City(StructuredNode):
    name = StringProperty(required=True)
    country = RelationshipTo(Country, "FROM_COUNTRY")


class Person(StructuredNode):
    uid = UniqueIdProperty()
    name = StringProperty(unique_index=True)
    age = IntegerProperty(index=True, default=0)

    # traverse outgoing IS_FROM relations, inflate to Country objects
    country = RelationshipTo(Country, "IS_FROM")

    # traverse outgoing LIVES_IN relations, inflate to City objects
    city = RelationshipTo(City, "LIVES_IN")


if __name__ == "__main__":
    torin = Person(name="Torin", age=34).save()

    print(torin)
