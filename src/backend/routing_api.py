"""
Hazard-Aware Safe Routing API (Member B - Prompt 3)
SIH26002 - MargSetu: Smart Logistics & Accessibility Platform

Provides GIS routing endpoints that calculate optimal hazard-avoiding paths across
the North Eastern Region road network, leveraging pgRouting/A* algorithms with dynamic cost mutation.

Exact pgRouting A* SQL Query:
```sql
SELECT 
    r.seq, r.node, r.edge, r.cost,
    e.segment_id, e.hazard_prob, e.length_km, e.dynamic_cost,
    ST_AsGeoJSON(e.geom) AS geom_json
FROM pgr_astar(
    'SELECT id, source, target, dynamic_cost AS cost, dynamic_reverse_cost AS reverse_cost,
            x1, y1, x2, y2 FROM road_edges',
    :source_node,
    :target_node,
    directed := true
) AS r
JOIN road_edges e ON r.edge = e.id
ORDER BY r.seq;
```
"""

import math
import heapq
from typing import List, Dict, Tuple, Optional, Any
from fastapi import APIRouter, Query, HTTPException, status
from pydantic import BaseModel, Field

from src.backend.db import db_instance

router = APIRouter(tags=["Routing Engine"])


# Response Schemas
class SegmentTraversedInfo(BaseModel):
    segment_id: str
    length_km: float
    base_cost_min: float
    dynamic_cost_min: float
    hazard_probability: float
    status: str


class SafeRouteResponse(BaseModel):
    source_node: int
    target_node: int
    total_distance_km: float
    total_travel_time_min: float
    segments_count: int
    region_isolated: bool
    isolation_warning: Optional[str] = None
    traversed_segments: List[SegmentTraversedInfo]
    route_geojson: Dict[str, Any]


def haversine_distance_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Calculates great-circle distance between two point coordinates in km."""
    r = 6371.0 # Earth radius km
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)

    a = math.sin(dphi / 2.0)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlng / 2.0)**2
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return r * c


def snap_coordinate_to_nearest_node(lat: float, lng: float) -> int:
    """
    Snaps arbitrary GPS coordinate to nearest graph node in road_edges table.
    """
    edges = db_instance.get_all_edges()
    best_node = None
    min_dist = float("inf")

    for edge in edges:
        # Check source node distance
        d_src = haversine_distance_km(lat, lng, edge["start_lat"], edge["start_lng"])
        if d_src < min_dist:
            min_dist = d_src
            best_node = edge["source"]

        # Check target node distance
        d_tgt = haversine_distance_km(lat, lng, edge["end_lat"], edge["end_lng"])
        if d_tgt < min_dist:
            min_dist = d_tgt
            best_node = edge["target"]

    return best_node if best_node is not None else 1


def compute_dijkstra_astar_route(source_node: int, target_node: int) -> Tuple[List[Dict[str, Any]], float, bool]:
    """
    Executes graph routing using mutated `dynamic_cost`.
    Returns (traversed_edges_list, total_cost, is_isolated).
    """
    edges = db_instance.get_all_edges()

    # Build adjacency list: {node: [(neighbor, edge_dict, cost), ...]}
    graph = {}
    for edge in edges:
        s, t, cost = edge["source"], edge["target"], edge["dynamic_cost"]
        rev_cost = edge["dynamic_reverse_cost"]

        if s not in graph: graph[s] = []
        if t not in graph: graph[t] = []

        graph[s].append((t, edge, cost))
        graph[t].append((s, edge, rev_cost))

    # Priority queue for Dijkstra / A*
    queue = [(0.0, source_node, [])]
    visited = {}

    best_path = None
    min_total_cost = float("inf")

    while queue:
        cost, current, path = heapq.heappop(queue)

        if current in visited and visited[current] <= cost:
            continue
        visited[current] = cost

        if current == target_node:
            best_path = path
            min_total_cost = cost
            break

        for neighbor, edge_info, edge_cost in graph.get(current, []):
            if neighbor not in visited or visited[neighbor] > cost + edge_cost:
                heapq.heappush(queue, (cost + edge_cost, neighbor, path + [edge_info]))

    if not best_path or min_total_cost >= 999999.0:
        # Region is isolated or all available paths cross blocked segments (dynamic_cost >= 999999)
        return [], 999999.0, True

    return best_path, min_total_cost, False


@router.get("/route-safe", response_model=SafeRouteResponse)
def get_safe_route(
    source_lat: float = Query(..., ge=-90.0, le=90.0, example=26.7271, description="Origin latitude"),
    source_lng: float = Query(..., ge=-180.0, le=180.0, example=88.3953, description="Origin longitude"),
    target_lat: float = Query(..., ge=-90.0, le=90.0, example=27.3389, description="Destination latitude"),
    target_lng: float = Query(..., ge=-180.0, le=180.0, example=88.6065, description="Destination longitude")
):
    """
    Calculates hazard-avoiding shortest path snapping coordinates to graph nodes.
    Returns GeoJSON LineString, segment list, and isolation warnings if region is cut off.
    """
    source_node = snap_coordinate_to_nearest_node(source_lat, source_lng)
    target_node = snap_coordinate_to_nearest_node(target_lat, target_lng)

    traversed_edges, total_cost, is_isolated = compute_dijkstra_astar_route(source_node, target_node)

    if is_isolated or not traversed_edges:
        # Return HTTP 200 with disaster-response warning payload as specified in Prompt 3
        return SafeRouteResponse(
            source_node=source_node,
            target_node=target_node,
            total_distance_km=0.0,
            total_travel_time_min=999999.0,
            segments_count=0,
            region_isolated=True,
            isolation_warning="CRITICAL DISASTER ALERT: Destination region is fully cut off by high-risk landslide blockages (hazard_prob >= 0.70). No safe highway corridor available.",
            traversed_segments=[],
            route_geojson={"type": "FeatureCollection", "features": []}
        )

    # Build GeoJSON feature collection
    coordinates = []
    traversed_info = []
    total_dist_km = 0.0
    total_time_min = 0.0

    for edge in traversed_edges:
        coordinates.append([edge["start_lng"], edge["start_lat"]])
        coordinates.append([edge["end_lng"], edge["end_lat"]])

        total_dist_km += edge["length_km"]
        # Travel time calculation (ignoring blocked state since route is valid)
        seg_time = edge["dynamic_cost"] if edge["dynamic_cost"] < 999999.0 else edge["cost"]
        total_time_min += seg_time

        haz_p = edge["hazard_prob"]
        status_label = "CRITICAL_AVOID" if haz_p >= 0.70 else ("WARNING_SLOW" if haz_p >= 0.35 else "SAFE")

        traversed_info.append(SegmentTraversedInfo(
            segment_id=edge["segment_id"],
            length_km=round(edge["length_km"], 2),
            base_cost_min=round(edge["cost"], 2),
            dynamic_cost_min=round(edge["dynamic_cost"], 2),
            hazard_probability=round(haz_p, 4),
            status=status_label
        ))

    geojson = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": coordinates
                },
                "properties": {
                    "source_node": source_node,
                    "target_node": target_node,
                    "total_distance_km": round(total_dist_km, 2),
                    "total_travel_time_min": round(total_time_min, 2)
                }
            }
        ]
    }

    return SafeRouteResponse(
        source_node=source_node,
        target_node=target_node,
        total_distance_km=round(total_dist_km, 2),
        total_travel_time_min=round(total_time_min, 2),
        segments_count=len(traversed_info),
        region_isolated=False,
        isolation_warning=None,
        traversed_segments=traversed_info,
        route_geojson=geojson
    )
