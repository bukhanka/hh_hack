-- Initialize database schema
-- This script runs automatically when the container is first created

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create tables (will be handled by SQLAlchemy, but we can add indexes here)
-- Additional optimizations can be added here

-- Create index for faster timestamp queries
CREATE INDEX IF NOT EXISTS idx_radar_runs_created_at ON radar_runs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_stories_hotness ON stories(hotness DESC);
CREATE INDEX IF NOT EXISTS idx_stories_radar_run_id ON stories(radar_run_id);

