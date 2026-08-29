# Prompts for Member B — Backend / Routing Engineer

Constraint baked into every prompt below: **CPU-only stack** — PostgreSQL+PostGIS+pgRouting, or OSRM, both pure-C++/SQL engines, no GPU anywhere.

---

### Prompt 1 — Database schema

```
Design a PostgreSQL + PostGIS schema for a road-hazard routing system with
these tables (write the full CREATE TABLE statements with appropriate
types, indexes, and foreign keys):

1. road_edges: id, source, target, geom (LineString), length_km,
   base_speed_kmh, cost, reverse_cost, hazard_prob, dynamic_cost,
   dynamic_reverse_cost, last_updated.
2. hazard_scores: segment_id (FK), timestamp, hazard_probability,
   model_version.
3. crowdsource_reports: id, segment_id (FK), reporter_id, photo_url,
   report_type (crack|flood|blockage|clear), lat, lng, submitted_at,
   synced_at, verified boolean.
4. vehicles: id, driver_name, current_lat, current_lng, last_ping_at.

Add a spatial GIST index on all geometry columns. Explain in 2-3
sentences why dynamic_cost is a separate column instead of overwriting
cost directly.
```

---

### Prompt 2 — Dynamic edge-weight update job

```
Write a SQL UPDATE statement (as used with pgRouting) that recalculates
dynamic_cost and dynamic_reverse_cost for the road_edges table based on
hazard_prob using this rule:
- hazard_prob >= 0.70  -> dynamic_cost = 999999 (effectively blocked)
- 0.35 <= hazard_prob < 0.70 -> dynamic_cost = cost * (1 + 5 * hazard_prob^2)
- hazard_prob < 0.35 -> dynamic_cost = cost (unchanged)

Then wrap it in a Python function using psycopg2 or SQLAlchemy that runs
this update every time new hazard scores arrive from the ML service
(Member A's /predict endpoint), and can be scheduled via a simple cron
or APScheduler job every 15 minutes. Include error handling for a
partial/failed hazard update (don't leave dynamic_cost half-updated).
```

---

### Prompt 3 — Safe-route API endpoint

```
Write a FastAPI router `routing.py` with:

GET /route-safe?source_lat=&source_lng=&target_lat=&target_lng=

that:
1. Snaps source/target coordinates to the nearest road_edges node.
2. Runs pgr_astar (or pgr_dijkstra if astar isn't set up) using
   dynamic_cost as the cost column.
3. Returns a GeoJSON LineString of the resulting route plus a list of
   segment_ids traversed and their hazard_probability, so the frontend
   can color-code the route.
4. If no route exists below the blocked threshold (all paths >=999999),
   return a 200 with a warning field explaining the region is fully cut
   off, rather than an error — this matters for a disaster-response UI.

Include the exact pgr_astar SQL query as a comment above the Python
function that calls it.
```

---

### Prompt 4 — OSRM alternative (if choosing OSRM over pgRouting)

```
Write a Python script `generate_osrm_traffic_file.py` that:
1. Queries road_edges where hazard_prob >= 0.35.
2. For hazard_prob >= 0.70, sets adjusted speed to 1 km/h (near-blocked).
3. For 0.35-0.70, reduces base_speed_kmh proportionally to
   (1 - hazard_prob^1.5).
4. Writes an OSRM segment-speed CSV: from_osm_node,to_osm_node,speed_kmh.
5. Calls `osrm-customize` via subprocess with --segment-speed-file
   pointing at that CSV, and logs success/failure.

Then write a matching profile.lua snippet that marks a way inaccessible
(mode.inaccessible) when a custom `hazard_factor` tag on the way is
>= 0.70. Comment clearly where a beginner would need to add the
custom tag during OSM data prep.
```

---

### Prompt 5 — Sync endpoints for the offline field app

```
Design and implement two FastAPI endpoints for offline-first sync:

POST /api/v1/sync/up
  body: a batch array of crowdsource_reports created offline (with a
  client-generated UUID and client_timestamp for each), possibly
  containing duplicates from retried uploads.
  behavior: upsert by UUID (idempotent), reject reports missing
  required fields, return per-item success/failure status.

GET /api/v1/sync/down?since=<ISO timestamp>
  behavior: returns all hazard_scores and road_edges changed since
  `since`, in a compact JSON payload suitable for a slow 2G connection
  (no unnecessary fields, geometry simplified to a lower precision).

Explain your conflict-resolution strategy (last-write-wins vs vector
timestamps) in a short comment block at the top of the file, and justify
the choice given this is emergency-response data where a false "all
clear" is worse than a false alarm.
```

---

### Prompt 6 — API gateway / rate limiting (optional, for polish)

```
Write a minimal Kong or Envoy config (or, if time is short, a FastAPI
middleware alternative) that adds: JWT auth on all /api/v1 routes except
/health, and basic rate limiting (60 req/min per API key) on
/route-safe. Keep this simple — we only need it to look production-ready
for the demo, not survive real traffic.
```
