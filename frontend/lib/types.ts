/**
 * TypeScript types for RADAR API
 */

export interface Entity {
  name: string;
  type: string; // company, ticker, sector, country, person
  relevance: number;
  ticker?: string;
}

export interface TimelineEvent {
  timestamp: string;
  description: string;
  source_url: string;
  event_type: string; // first_mention, confirmation, update, correction
}

export interface HotnessScore {
  overall: number;
  unexpectedness: number;
  materiality: number;
  velocity: number;
  breadth: number;
  credibility: number;
  reasoning: string;
}

export interface NewsStory {
  id: string;
  headline: string;
  hotness: number;
  hotness_details: HotnessScore;
  why_now: string;
  entities: Entity[];
  sources: string[];
  timeline: TimelineEvent[];
  draft: string;
  dedup_group: string;
  created_at: string;
  article_count: number;
  has_deep_research: boolean;
  research_summary?: string;
}

export interface RadarResponse {
  stories: NewsStory[];
  total_articles_processed: number;
  time_window_hours: number;
  generated_at: string;
  processing_time_seconds: number;
}

export interface ProcessRequest {
  time_window_hours?: number;
  top_k?: number;
  hotness_threshold?: number;
  custom_feeds?: string[];
}

export interface HealthResponse {
  status: string;
  version: string;
  google_api_configured: boolean;
}

export interface RadarRun {
  id: number;
  created_at: string;
  time_window_hours: number;
  total_articles_processed: number;
  processing_time_seconds: number;
  hotness_threshold: number;
  top_k: number;
  story_count: number;
}

export interface HistoryResponse {
  history: RadarRun[];
  limit: number;
  offset: number;
}

export interface RunDetailsResponse extends RadarRun {
  stories: NewsStory[];
}

// ============================================================================
// Personal News Aggregator Types
// ============================================================================

export interface PersonalNewsItem {
  id: string;
  title: string;
  summary: string;
  url: string;
  source: string;
  published_at: string;
  author?: string;
  image_url?: string;
  relevance_score: number;
  matched_keywords: string[];
  cluster_size: number;
}

export interface PersonalFeedResponse {
  items: PersonalNewsItem[];
  total_articles_processed: number;
  filtered_count: number;
  time_window_hours: number;
  generated_at: string;
  processing_time_seconds: number;
  user_id?: string;
}

export interface UserPreferences {
  user_id: string;
  sources: string[];
  keywords: string[];
  excluded_keywords: string[];
  categories: string[];
  update_frequency_minutes: number;
  max_articles_per_feed: number;
  language: string;
  created_at: string;
  updated_at: string;
}

export interface PersonalScanRequest {
  user_id?: string;
  time_window_hours?: number;
  custom_sources?: string[];
}

export interface RSSSource {
  name: string;
  url: string;
}

// ============================================================================
// Interactions & Feed Storage Types
// ============================================================================

export interface InteractionRequest {
  user_id: string;
  article_id: string;
  interaction_type: 'view' | 'click' | 'like' | 'dislike' | 'save' | 'unlike' | 'undislike' | 'unsave';
  view_duration_seconds?: number;
  scroll_depth?: number;
  clicked_read_more?: boolean;
  matched_keywords?: string[];
  relevance_score?: number;
}

export interface FeedItem {
  id: number;
  user_id: string;
  article_id: string;
  title: string;
  summary: string;
  url: string;
  source: string;
  published_at: string;
  added_to_feed_at: string;
  relevance_score: number;
  matched_keywords: string[];
  cluster_size: number;
  is_read: boolean;
  is_liked: boolean;
  is_disliked: boolean;
  is_saved: boolean;
  read_at?: string;
  liked_at?: string;
  disliked_at?: string;
  saved_at?: string;
}

export interface UserStats {
  user_id: string;
  days: number;
  total_articles_in_feed: number;
  articles_read: number;
  articles_liked: number;
  articles_saved: number;
  total_interactions: number;
  avg_view_duration_seconds: number;
}

// ============================================================================
// Onboarding Types
// ============================================================================

export interface OnboardingPreset {
  id?: number;
  preset_key: string;
  name: string;
  emoji: string;
  description: string;
  categories: string[];
  keywords: string[];
  sources: string[];
  sort_order: number;
  is_active: boolean;
}

export interface OnboardingCompleteRequest {
  user_id: string;
  preset_key?: string;
  categories: string[];
  keywords: string[];
  sources: string[];
}

export interface OnboardingStatus {
  user_id: string;
  onboarding_completed: boolean;
  has_profile: boolean;
}

// ============================================================================
// Learning Engine & Smart Feed Types
// ============================================================================

export interface KeywordWeight {
  keyword: string;
  weight: number;
  engagement_count: number;
  last_seen_at: string;
}

export interface KeywordWeightsResponse {
  user_id: string;
  weights: Record<string, number>;
}

export interface UpdateWeightsResponse {
  message: string;
  weights: Record<string, number>;
}

export interface LearningInsights {
  total_learned_keywords: number;
  strong_interests: [string, number][];
  moderate_interests: [string, number][];
  weak_interests: [string, number][];
  learning_status: 'active' | 'learning';
}

export interface DiscoverInterestsResponse {
  user_id: string;
  suggested_keywords: string[];
  count: number;
}

// ============================================================================
// Background Worker Types
// ============================================================================

export interface BackgroundJobInfo {
  id: string;
  name: string;
  next_run: string | null;
  trigger: string;
}

export interface WorkerStatusResponse {
  is_running: boolean;
  jobs: BackgroundJobInfo[];
  total_jobs: number;
}

export interface JobExecutionResponse {
  message: string;
}

// ============================================================================
// Feed Update & Refresh Types
// ============================================================================

export interface NewItemsCountResponse {
  new_items_count: number;
  since: string;
  latest_update: string | null;
  checked_at: string;
}

export interface FeedMetadata {
  total_items: number;
  unread_items: number;
  latest_update: string | null;
  last_check: string | null;
  last_active: string | null;
}

export interface RefreshFeedResponse {
  message: string;
  new_items_added: number;
  total_items: number;
  items: any[];
}

