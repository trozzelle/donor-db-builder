from gqlalchemy import Memgraph, Node, Relationship


class Filer(Node):
    filer_id: int
    name: str
    type: str
    status: str
    office: str
    district: str
    county: str
    municipality: str
    subdivision: str


# MERGE(c: Committee
# {filer_id: $filer_id})
# SET
# c.name = $name,
# c.type = $type,
# c.status = $status,
# c.office = $office,
# c.district = $district,
# c.county = $county,
# c.municipality = $municipality,
# c.subdivision = $subdivision