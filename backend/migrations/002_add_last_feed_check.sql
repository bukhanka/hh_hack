-- Migration: Add last_feed_check column to user_profiles
-- This field tracks when user last checked their feed for new items notification

ALTER TABLE user_profiles 
ADD COLUMN IF NOT EXISTS last_feed_check TIMESTAMP;

-- Create index for faster queries
CREATE INDEX IF NOT EXISTS idx_user_profiles_last_feed_check 
ON user_profiles(last_feed_check);

-- Add comment
COMMENT ON COLUMN user_profiles.last_feed_check IS 'Timestamp of when user last checked their feed (for new items notification)';

