-- PostgreSQL + PostGIS Schema for MargSetu Road-Hazard Routing System
-- SIH26002 - Smart Logistics & Accessibility Platform

-- Enable PostGIS and pgRouting extensions
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS pgrouting;

-- 1. Road Edges Table
CREATE TABLE IF NOT EXISTS road_edges (
    id SERIAL PRIMARY KEY,
    segment_id VARCHAR(64) UNIQUE NOT NULL,
    source INTEGER NOT NULL,
    target INTEGER NOT NULL,
    geom GEOMETRY(LineString, 4326) NOT NULL,
    length_km DOUBLE PRECISION NOT NULL,
    base_speed_kmh DOUBLE PRECISION NOT NULL DEFAULT 40.0,
    cost DOUBLE PRECISION NOT NULL, -- Base travel cost in minutes
    reverse_cost DOUBLE PRECISION NOT NULL,
    hazard_prob DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    dynamic_cost DOUBLE PRECISION NOT NULL,
    dynamic_reverse_cost DOUBLE PRECISION NOT NULL,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Spatial GIST index on road edge geometry
CREATE INDEX IF NOT EXISTS idx_road_edges_geom ON road_edges USING GIST(geom);
CREATE INDEX IF NOT EXISTS idx_road_edges_source_target ON road_edges(source, target);

-- 2. Hazard Scores History Table
CREATE TABLE IF NOT EXISTS hazard_scores (
    id SERIAL PRIMARY KEY,
    segment_id VARCHAR(64) NOT NULL REFERENCES road_edges(segment_id) ON DELETE CASCADE,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    hazard_probability DOUBLE PRECISION NOT NULL,
    model_version VARCHAR(32) NOT NULL DEFAULT 'xgb-1.0'
);

CREATE INDEX IF NOT EXISTS idx_hazard_scores_segment_ts ON hazard_scores(segment_id, timestamp DESC);

-- 3. Crowdsource Reports Table (Offline Sync & Field Uploads)
CREATE TABLE IF NOT EXISTS crowdsource_reports (
    id UUID PRIMARY KEY,
    segment_id VARCHAR(64) REFERENCES road_edges(segment_id) ON DELETE SET NULL,
    reporter_id VARCHAR(64) NOT NULL,
    photo_url TEXT,
    report_type VARCHAR(32) NOT NULL CHECK (report_type IN ('crack', 'flood', 'blockage', 'clear')),
    lat DOUBLE PRECISION NOT NULL,
    lng DOUBLE PRECISION NOT NULL,
    submitted_at TIMESTAMP WITH TIME ZONE NOT NULL,
    synced_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    verified BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE INDEX IF NOT EXISTS idx_crowdsource_reports_submitted ON crowdsource_reports(submitted_at DESC);
CREATE INDEX IF NOT EXISTS idx_crowdsource_reports_segment ON crowdsource_reports(segment_id);

-- 4. Vehicles Tracking Table
CREATE TABLE IF NOT EXISTS vehicles (
    id VARCHAR(64) PRIMARY KEY,
    driver_name VARCHAR(128) NOT NULL,
    current_lat DOUBLE PRECISION NOT NULL,
    current_lng DOUBLE PRECISION NOT NULL,
    last_ping_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

/*
===============================================================================
SCHEMA DESIGN EXPLANATION:
Why `dynamic_cost` is a separate column instead of overwriting `cost` directly:
-------------------------------------------------------------------------------
1. Base `cost` reflects structural physical highway properties (segment distance
   and design speed limit), which remain constant regardless of weather events.
2. `dynamic_cost` represents weather/landslide mutated operational travel cost.
   Keeping base `cost` preserved allows instant recovery back to baseline when
   a hazard clears (hazard_prob < 0.35) without needing external lookup tables.
3. Allows multi-modal routing comparisons (e.g. "Normal route time: 45 min vs.
   Hazard-avoidance route time: 62 min").
===============================================================================
*/
