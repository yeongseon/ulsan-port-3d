from app.schemas.common import APIModel


class GraphNode(APIModel):
    type: str
    id: str
    label: str
    data: dict[str, str | int | float | bool | None] | None = None


class GraphEdge(APIModel):
    source_type: str
    source_id: str
    target_type: str
    target_id: str
    predicate: str


class EntityGraphRelation(APIModel):
    predicate: str
    direction: str
    node: GraphNode


class EntityGraphResponse(APIModel):
    center: GraphNode
    relations: list[EntityGraphRelation]


class GraphExploreResponse(APIModel):
    nodes: list[GraphNode]
    edges: list[GraphEdge]
