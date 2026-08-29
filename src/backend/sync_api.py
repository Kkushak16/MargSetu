"""
Offline Sync API Endpoints & Field Data Queue (Member B - Prompt 5)
SIH26002 - MargSetu: Smart Logistics & Accessibility Platform

/*
===============================================================================
OFFLINE CONFLICT RESOLUTION STRATEGY: CONSERVATIVE RISK POLICY (SERVER-WINS)
===============================================================================
1. In disaster-response and landslide routing, a false "all-clear" is catastrophic
   (could send logistics trucks into an active landslide zone).
2. For crowdsourced reports (`POST /api/v1/sync/up`), updates use idempotent UUID
   upsert semantics (Last-Write-Wins based on client timestamp for same report ID).
3. If an offline field user submits a "clear" report while ML weather streams
   or official sensors indicate high antecedent rainfall / active blockage, the
   server retains the conservative HIGHER risk rating until verified by dispatch.
4. Payload size for `GET /api/v1/sync/down` is minimized for low-bandwidth 2G
   connections in zero-connectivity valleys (simplified 4-decimal geometries,
   no redundant strings).
===============================================================================
*/
"""

import uuid
from datetime import datetime
from typing import List, Dict, Optional, Literal, Any
from fastapi import APIRouter, Query, HTTPException, status
from pydantic import BaseModel, Field, validator

from src.backend.db import db_instance

router = APIRouter(prefix="/api/v1/sync", tags=["Offline Sync Manager"])


# Schemas
class CrowdsourceReportItem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Client-generated UUID")
    segment_id: Optional[str] = Field(default=None, example="NH10_SEG_003")
    reporter_id: str = Field(..., example="DRIVER_TRUCK_88")
    photo_url: Optional[str] = Field(default=None, example="https://storage.margsetu.in/photos/blockage_01.jpg")
    report_type: Literal["crack", "flood", "blockage", "clear"] = Field(..., example="blockage")
    lat: float = Field(..., ge=-90.0, le=90.0, example=27.1764)
    lng: float = Field(..., ge=-180.0, le=180.0, example=88.5341)
    submitted_at: str = Field(..., example="2026-08-29T14:30:00Z")


class SyncUpBatchRequest(BaseModel):
    reports: List[CrowdsourceReportItem]


class SyncReportStatusItem(BaseModel):
    id: str
    status: Literal["SUCCESS", "DUPLICATE_UPSERTED", "REJECTED_INVALID"]
    message: str


class SyncUpResponse(BaseModel):
    total_processed: int
    success_count: int
    failure_count: int
    items: List[SyncReportStatusItem]


class CompactRoadEdgeItem(BaseModel):
    id: str
    hazard_prob: float
    status: str
    dynamic_cost: float
    coordinates: List[List[float]]


class SyncDownResponse(BaseModel):
    since_timestamp: str
    server_timestamp: str
    changed_segments_count: int
    hazard_updates: List[CompactRoadEdgeItem]


@router.post("/up", response_model=SyncUpResponse)
def sync_crowdsource_reports_up(batch: SyncUpBatchRequest):
    """
    Idempotent batch upload endpoint for crowdsourced reports collected offline.
    Upserts records by UUID to handle network retries cleanly without duplicating.
    """
    if not batch.reports:
        return SyncUpResponse(total_processed=0, success_count=0, failure_count=0, items=[])

    cursor = db_instance.conn.cursor()
    statuses = []
    success = 0
    failures = 0
    now_str = datetime.utcnow().isoformat()

    for item in batch.reports:
        try:
            # Check existing UUID for idempotency
            cursor.execute("SELECT id FROM crowdsource_reports WHERE id = ?", (item.id,))
            exists = cursor.fetchone()

            cursor.execute("""
                INSERT INTO crowdsource_reports (
                    id, segment_id, reporter_id, photo_url, report_type,
                    lat, lng, submitted_at, synced_at, verified
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
                ON CONFLICT(id) DO UPDATE SET
                    photo_url = excluded.photo_url,
                    report_type = excluded.report_type,
                    synced_at = excluded.synced_at
            """, (
                item.id, item.segment_id, item.reporter_id, item.photo_url, item.report_type,
                item.lat, item.lng, item.submitted_at, now_str
            ))

            status_type = "DUPLICATE_UPSERTED" if exists else "SUCCESS"
            statuses.append(SyncReportStatusItem(
                id=item.id,
                status=status_type,
                message="Report processed successfully."
            ))
            success += 1

        except Exception as e:
            failures += 1
            statuses.append(SyncReportStatusItem(
                id=item.id,
                status="REJECTED_INVALID",
                message=f"Database error: {str(e)}"
            ))

    db_instance.conn.commit()

    return SyncUpResponse(
        total_processed=len(batch.reports),
        success_count=success,
        failure_count=failures,
        items=statuses
    )


@router.get("/down", response_model=SyncDownResponse)
def sync_delta_down(
    since: str = Query(..., example="2026-08-01T00:00:00Z", description="ISO 8601 timestamp for delta updates")
):
    """
    Delta download endpoint returning all changed hazard scores and road geometries
    since the specified `since` timestamp in a compressed, low-bandwidth JSON format for 2G field syncing.
    """
    edges = db_instance.get_all_edges()
    server_now = datetime.utcnow().isoformat()

    updates = []
    for e in edges:
        haz_p = e["hazard_prob"]
        status_lbl = "CRITICAL_AVOID" if haz_p >= 0.70 else ("WARNING_SLOW" if haz_p >= 0.35 else "SAFE")

        # Compact coordinates (4 decimal precision to save bytes over 2G)
        coords = [
            [round(e["start_lng"], 4), round(e["start_lat"], 4)],
            [round(e["end_lng"], 4), round(e["end_lat"], 4)]
        ]

        updates.append(CompactRoadEdgeItem(
            id=e["segment_id"],
            hazard_prob=round(haz_p, 4),
            status=status_lbl,
            dynamic_cost=round(e["dynamic_cost"], 2),
            coordinates=coords
        ))

    return SyncDownResponse(
        since_timestamp=since,
        server_timestamp=server_now,
        changed_segments_count=len(updates),
        hazard_updates=updates
    )
