from collections import deque

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.documents import Alert, HazardDoc, MsdsDoc
from app.models.static import Berth, Buoy, CargoType, Operator, PortZone, RouteSegment, TankTerminal
from app.models.timeseries import (
    CargoStatMonthly,
    LatestBerthStatus,
    LatestVesselPosition,
    TideObservation,
    VesselEvent,
    WeatherObservation,
)
from app.schemas.graph import (
    EntityGraphRelation,
    EntityGraphResponse,
    GraphEdge,
    GraphExploreResponse,
    GraphNode,
)
from app.services.common import not_found, parse_uuid_or_none, stringify_id, to_utc_iso


class RelatedNode:
    def __init__(self, *, predicate: str, direction: str, node: GraphNode) -> None:
        self.predicate = predicate
        self.direction = direction
        self.node = node


def _graph_node(
    *,
    entity_type: str,
    entity_id: str,
    label: str,
    data: dict[str, str | int | float | bool | None] | None = None,
) -> GraphNode:
    return GraphNode(type=entity_type, id=entity_id, label=label, data=data)


async def _load_port(entity_id: str) -> GraphNode:
    if entity_id != "ulsan-port":
        raise not_found(f"Port '{entity_id}' was not found.")
    return _graph_node(entity_type="Port", entity_id=entity_id, label="울산항")


async def _load_zone(db: AsyncSession, entity_id: str) -> GraphNode:
    zone_uuid = parse_uuid_or_none(entity_id)
    zone = await db.get(PortZone, zone_uuid) if zone_uuid is not None else None
    if zone is None:
        raise not_found(f"Zone '{entity_id}' was not found.")
    return _graph_node(
        entity_type="Zone",
        entity_id=stringify_id(zone.zone_id),
        label=zone.name,
        data={"zone_type": zone.zone_type, "created_at": to_utc_iso(zone.created_at)},
    )


async def _load_berth(db: AsyncSession, entity_id: str) -> GraphNode:
    berth_uuid = parse_uuid_or_none(entity_id)
    stmt = select(Berth).where(Berth.facility_code == entity_id)
    if berth_uuid is not None:
        stmt = select(Berth).where(
            (Berth.berth_id == berth_uuid) | (Berth.facility_code == entity_id)
        )
    berth = await db.scalar(stmt)
    if berth is None:
        raise not_found(f"Berth '{entity_id}' was not found.")
    return _graph_node(
        entity_type="Berth",
        entity_id=stringify_id(berth.berth_id),
        label=berth.name,
        data={"facility_code": berth.facility_code, "depth": berth.depth, "length": berth.length},
    )


async def _load_operator(db: AsyncSession, entity_id: str) -> GraphNode:
    operator_uuid = parse_uuid_or_none(entity_id)
    operator = await db.get(Operator, operator_uuid) if operator_uuid is not None else None
    if operator is None:
        raise not_found(f"Operator '{entity_id}' was not found.")
    return _graph_node(
        entity_type="Operator",
        entity_id=stringify_id(operator.operator_id),
        label=operator.name,
        data={"operator_type": operator.operator_type},
    )


async def _load_vessel(db: AsyncSession, entity_id: str) -> GraphNode:
    vessel = await db.get(LatestVesselPosition, entity_id)
    if vessel is None:
        raise not_found(f"Vessel '{entity_id}' was not found.")
    return _graph_node(
        entity_type="Vessel",
        entity_id=vessel.vessel_id,
        label=vessel.name or vessel.vessel_id,
        data={"ship_type": vessel.ship_type, "observed_at": to_utc_iso(vessel.observed_at)},
    )


async def _load_cargo_type(db: AsyncSession, entity_id: str) -> GraphNode:
    cargo_uuid = parse_uuid_or_none(entity_id)
    cargo = await db.get(CargoType, cargo_uuid) if cargo_uuid is not None else None
    if cargo is None:
        raise not_found(f"CargoType '{entity_id}' was not found.")
    return _graph_node(
        entity_type="CargoType",
        entity_id=stringify_id(cargo.cargo_type_id),
        label=cargo.name,
        data={"category": cargo.category},
    )


async def _load_default(db: AsyncSession, entity_type: str, entity_id: str) -> GraphNode:
    if entity_type == "Port":
        return await _load_port(entity_id)
    if entity_type == "Zone":
        return await _load_zone(db, entity_id)
    if entity_type == "Berth":
        return await _load_berth(db, entity_id)
    if entity_type == "Operator":
        return await _load_operator(db, entity_id)
    if entity_type == "Vessel":
        return await _load_vessel(db, entity_id)
    if entity_type == "CargoType":
        return await _load_cargo_type(db, entity_id)
    return _graph_node(entity_type=entity_type, entity_id=entity_id, label=entity_id)


async def _related_for_port(db: AsyncSession) -> list[RelatedNode]:
    zones = (await db.scalars(select(PortZone).order_by(PortZone.name.asc()))).all()
    return [
        RelatedNode(
            predicate="hasZone",
            direction="outgoing",
            node=_graph_node(
                entity_type="Zone", entity_id=stringify_id(zone.zone_id), label=zone.name
            ),
        )
        for zone in zones
    ]


async def _related_for_zone(db: AsyncSession, entity_id: str) -> list[RelatedNode]:
    zone_uuid = parse_uuid_or_none(entity_id)
    zone = await db.get(PortZone, zone_uuid) if zone_uuid is not None else None
    if zone is None:
        raise not_found(f"Zone '{entity_id}' was not found.")

    berths = (await db.scalars(select(Berth).where(Berth.zone_id == zone.zone_id))).all()
    buoys = (await db.scalars(select(Buoy).where(Buoy.zone_id == zone.zone_id))).all()
    routes = (
        await db.scalars(select(RouteSegment).where(RouteSegment.zone_id == zone.zone_id))
    ).all()
    tanks = (
        await db.scalars(select(TankTerminal).where(TankTerminal.zone_id == zone.zone_id))
    ).all()
    weather = (
        await db.scalars(
            select(WeatherObservation)
            .where(WeatherObservation.zone_name == zone.name)
            .order_by(WeatherObservation.observed_at.desc())
            .limit(5)
        )
    ).all()
    tides = (
        await db.scalars(
            select(TideObservation).order_by(TideObservation.observed_at.desc()).limit(3)
        )
    ).all()

    related: list[RelatedNode] = [
        RelatedNode(
            predicate="hasZone",
            direction="incoming",
            node=_graph_node(entity_type="Port", entity_id="ulsan-port", label="울산항"),
        )
    ]
    related.extend(
        RelatedNode(
            predicate="hasBerth",
            direction="outgoing",
            node=_graph_node(
                entity_type="Berth", entity_id=stringify_id(item.berth_id), label=item.name
            ),
        )
        for item in berths
    )
    related.extend(
        RelatedNode(
            predicate="hasBuoy",
            direction="outgoing",
            node=_graph_node(
                entity_type="Buoy", entity_id=stringify_id(item.buoy_id), label=item.name
            ),
        )
        for item in buoys
    )
    related.extend(
        RelatedNode(
            predicate="hasRouteSegment",
            direction="outgoing",
            node=_graph_node(
                entity_type="RouteSegment",
                entity_id=stringify_id(item.segment_id),
                label=item.name,
            ),
        )
        for item in routes
    )
    related.extend(
        RelatedNode(
            predicate="locatedIn",
            direction="incoming",
            node=_graph_node(
                entity_type="TankTerminal",
                entity_id=stringify_id(item.tank_terminal_id),
                label=item.name,
            ),
        )
        for item in tanks
    )
    related.extend(
        RelatedNode(
            predicate="hasWeather",
            direction="outgoing",
            node=_graph_node(
                entity_type="WeatherObservation",
                entity_id=str(item.id),
                label=f"{zone.name} weather {to_utc_iso(item.observed_at) or ''}".strip(),
            ),
        )
        for item in weather
    )
    related.extend(
        RelatedNode(
            predicate="hasTide",
            direction="outgoing",
            node=_graph_node(
                entity_type="TideObservation",
                entity_id=str(item.id),
                label=item.station_name or f"Tide {item.id}",
            ),
        )
        for item in tides
    )
    return related


async def _related_for_berth(db: AsyncSession, entity_id: str) -> list[RelatedNode]:
    berth_uuid = parse_uuid_or_none(entity_id)
    stmt = select(Berth).where(Berth.facility_code == entity_id)
    if berth_uuid is not None:
        stmt = select(Berth).where(
            (Berth.berth_id == berth_uuid) | (Berth.facility_code == entity_id)
        )
    berth = await db.scalar(stmt)
    if berth is None:
        raise not_found(f"Berth '{entity_id}' was not found.")

    zone = await db.get(PortZone, berth.zone_id)
    operator = await db.get(Operator, berth.operator_id) if berth.operator_id else None
    latest_status = await db.get(LatestBerthStatus, berth.facility_code)
    cargo_names = (
        await db.scalars(
            select(CargoStatMonthly.cargo_type)
            .where(CargoStatMonthly.berth_name == berth.name)
            .distinct()
        )
    ).all()
    cargoes = (
        (
            await db.scalars(
                select(CargoType).where(CargoType.name.in_([name for name in cargo_names if name]))
            )
        ).all()
        if cargo_names
        else []
    )

    related: list[RelatedNode] = []
    if zone is not None:
        related.append(
            RelatedNode(
                predicate="hasBerth",
                direction="incoming",
                node=_graph_node(
                    entity_type="Zone", entity_id=stringify_id(zone.zone_id), label=zone.name
                ),
            )
        )
    if operator is not None:
        related.append(
            RelatedNode(
                predicate="operates",
                direction="incoming",
                node=_graph_node(
                    entity_type="Operator",
                    entity_id=stringify_id(operator.operator_id),
                    label=operator.name,
                ),
            )
        )
    if latest_status is not None:
        related.append(
            RelatedNode(
                predicate="hasStatus",
                direction="outgoing",
                node=_graph_node(
                    entity_type="BerthStatus",
                    entity_id=latest_status.berth_facility_code,
                    label=latest_status.status,
                ),
            )
        )
    related.extend(
        RelatedNode(
            predicate="handlesCargo",
            direction="outgoing",
            node=_graph_node(
                entity_type="CargoType",
                entity_id=stringify_id(item.cargo_type_id),
                label=item.name,
            ),
        )
        for item in cargoes
    )
    return related


async def _related_for_operator(db: AsyncSession, entity_id: str) -> list[RelatedNode]:
    operator_uuid = parse_uuid_or_none(entity_id)
    operator = await db.get(Operator, operator_uuid) if operator_uuid is not None else None
    if operator is None:
        raise not_found(f"Operator '{entity_id}' was not found.")

    berths = (
        await db.scalars(select(Berth).where(Berth.operator_id == operator.operator_id))
    ).all()
    tanks = (
        await db.scalars(
            select(TankTerminal).where(TankTerminal.operator_id == operator.operator_id)
        )
    ).all()
    docs = (
        await db.scalars(
            select(HazardDoc).where(HazardDoc.source_page.ilike(f"%{operator.name}%")).limit(10)
        )
    ).all()

    related: list[RelatedNode] = [
        RelatedNode(
            predicate="operates",
            direction="outgoing",
            node=_graph_node(
                entity_type="Berth", entity_id=stringify_id(item.berth_id), label=item.name
            ),
        )
        for item in berths
    ]
    related.extend(
        RelatedNode(
            predicate="operates",
            direction="outgoing",
            node=_graph_node(
                entity_type="TankTerminal",
                entity_id=stringify_id(item.tank_terminal_id),
                label=item.name,
            ),
        )
        for item in tanks
    )
    related.extend(
        RelatedNode(
            predicate="hasHazardDoc",
            direction="outgoing",
            node=_graph_node(entity_type="HazardDoc", entity_id=str(item.doc_id), label=item.title),
        )
        for item in docs
    )
    return related


async def _related_for_vessel(db: AsyncSession, entity_id: str) -> list[RelatedNode]:
    vessel = await db.get(LatestVesselPosition, entity_id)
    if vessel is None:
        raise not_found(f"Vessel '{entity_id}' was not found.")

    events = (
        await db.scalars(
            select(VesselEvent)
            .where(VesselEvent.vessel_id == vessel.vessel_id)
            .order_by(VesselEvent.event_time.desc())
            .limit(10)
        )
    ).all()
    related = [
        RelatedNode(
            predicate="hasPosition",
            direction="outgoing",
            node=_graph_node(
                entity_type="VesselPosition",
                entity_id=vessel.vessel_id,
                label=to_utc_iso(vessel.observed_at) or vessel.vessel_id,
            ),
        )
    ]
    related.extend(
        RelatedNode(
            predicate="hasEvent",
            direction="outgoing",
            node=_graph_node(
                entity_type="VesselEvent",
                entity_id=str(item.event_id),
                label=f"{item.event_type} {to_utc_iso(item.event_time) or ''}".strip(),
            ),
        )
        for item in events
    )
    return related


async def _related_for_cargo_type(db: AsyncSession, entity_id: str) -> list[RelatedNode]:
    cargo_uuid = parse_uuid_or_none(entity_id)
    cargo = await db.get(CargoType, cargo_uuid) if cargo_uuid is not None else None
    if cargo is None:
        raise not_found(f"CargoType '{entity_id}' was not found.")

    docs = (await db.scalars(select(MsdsDoc).where(MsdsDoc.cargo_type == cargo.name))).all()
    berth_names = (
        await db.scalars(
            select(CargoStatMonthly.berth_name)
            .where(CargoStatMonthly.cargo_type == cargo.name)
            .distinct()
        )
    ).all()
    berth_name_values = [name for name in berth_names if name is not None]
    berths = (
        (await db.scalars(select(Berth).where(Berth.name.in_(berth_name_values)))).all()
        if berth_name_values
        else []
    )

    related: list[RelatedNode] = [
        RelatedNode(
            predicate="hasMsds",
            direction="outgoing",
            node=_graph_node(entity_type="MsdsDoc", entity_id=str(item.doc_id), label=item.title),
        )
        for item in docs
    ]
    related.extend(
        RelatedNode(
            predicate="handlesCargo",
            direction="incoming",
            node=_graph_node(
                entity_type="Berth", entity_id=stringify_id(item.berth_id), label=item.name
            ),
        )
        for item in berths
    )
    return related


async def _related_for_alert(db: AsyncSession, entity_id: str) -> list[RelatedNode]:
    alert_uuid = parse_uuid_or_none(entity_id)
    alert = await db.get(Alert, alert_uuid) if alert_uuid is not None else None
    if alert is None:
        raise not_found(f"Alert '{entity_id}' was not found.")
    if alert.related_entity_type and alert.related_entity_id:
        return [
            RelatedNode(
                predicate="relatesTo",
                direction="outgoing",
                node=_graph_node(
                    entity_type=alert.related_entity_type,
                    entity_id=alert.related_entity_id,
                    label=alert.related_entity_id,
                ),
            )
        ]
    return []


async def _get_related_nodes(
    db: AsyncSession, entity_type: str, entity_id: str
) -> list[RelatedNode]:
    if entity_type == "Port":
        return await _related_for_port(db)
    if entity_type == "Zone":
        return await _related_for_zone(db, entity_id)
    if entity_type == "Berth":
        return await _related_for_berth(db, entity_id)
    if entity_type == "Operator":
        return await _related_for_operator(db, entity_id)
    if entity_type == "Vessel":
        return await _related_for_vessel(db, entity_id)
    if entity_type == "CargoType":
        return await _related_for_cargo_type(db, entity_id)
    if entity_type == "Alert":
        return await _related_for_alert(db, entity_id)
    return []


async def get_entity_graph(
    db: AsyncSession, *, entity_type: str, entity_id: str
) -> EntityGraphResponse:
    center = await _load_default(db, entity_type, entity_id)
    related = await _get_related_nodes(db, entity_type, center.id)
    return EntityGraphResponse(
        center=center,
        relations=[
            EntityGraphRelation(predicate=item.predicate, direction=item.direction, node=item.node)
            for item in related
        ],
    )


async def explore_graph(
    db: AsyncSession,
    *,
    entity_type: str | None,
    entity_id: str | None,
    depth: int,
    direction: str,
) -> GraphExploreResponse:
    root_type = entity_type or "Port"
    root_id = entity_id or "ulsan-port"
    root = await _load_default(db, root_type, root_id)
    max_depth = max(1, min(depth, 3))

    nodes: dict[tuple[str, str], GraphNode] = {(root.type, root.id): root}
    edges: dict[tuple[str, str, str, str, str], GraphEdge] = {}
    queue = deque([(root, 0)])
    visited = {(root.type, root.id)}

    while queue:
        current, current_depth = queue.popleft()
        if current_depth >= max_depth:
            continue

        related = await _get_related_nodes(db, current.type, current.id)
        for item in related:
            if direction != "both" and item.direction != direction:
                continue

            nodes[(item.node.type, item.node.id)] = item.node
            if item.direction == "incoming":
                edge = GraphEdge(
                    source_type=item.node.type,
                    source_id=item.node.id,
                    target_type=current.type,
                    target_id=current.id,
                    predicate=item.predicate,
                )
            else:
                edge = GraphEdge(
                    source_type=current.type,
                    source_id=current.id,
                    target_type=item.node.type,
                    target_id=item.node.id,
                    predicate=item.predicate,
                )
            edges[
                (edge.source_type, edge.source_id, edge.target_type, edge.target_id, edge.predicate)
            ] = edge

            node_key = (item.node.type, item.node.id)
            if node_key not in visited and current_depth + 1 < max_depth:
                visited.add(node_key)
                queue.append((item.node, current_depth + 1))

    return GraphExploreResponse(nodes=list(nodes.values()), edges=list(edges.values()))
