/**
 * API client for RADAR backend
 */

import axios from 'axios';
import { logger } from './logger';
import type { 
  RadarResponse, 
  ProcessRequest, 
  HealthResponse, 
  HistoryResponse, 
  RunDetailsResponse,
  PersonalFeedResponse,
  PersonalScanRequest,
  UserPreferences,
  RSSSource,
  InteractionRequest,
  FeedItem,
  UserStats,
  OnboardingPreset,
  OnboardingCompleteRequest,
  OnboardingStatus,
  KeywordWeightsResponse,
  UpdateWeightsResponse,
  LearningInsights,
  DiscoverInterestsResponse,
  WorkerStatusResponse,
  JobExecutionResponse,
  NewItemsCountResponse,
  FeedMetadata,
  RefreshFeedResponse
} from './types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    logger.apiRequest(config.url || '', config.method?.toUpperCase() || '', config.params || config.data);
    return config;
  },
  (error) => {
    logger.apiError('Request failed', error);
    return Promise.reject(error);
  }
);

// Response interceptor for logging
api.interceptors.response.use(
  (response) => {
    logger.apiResponse(response.config.url || '', response.status, response.data);
    return response;
  },
  (error) => {
    const endpoint = error.config?.url || 'unknown';
    const status = error.response?.status || 'no response';
    logger.apiError(`${endpoint} [${status}]`, error);
    return Promise.reject(error);
  }
);

export const radarApi = {
  /**
   * Health check
   */
  async healthCheck(): Promise<HealthResponse> {
    const response = await api.get<HealthResponse>('/api/health');
    return response.data;
  },

  /**
   * Process news and get hot stories
   */
  async processNews(request: ProcessRequest): Promise<RadarResponse> {
    const response = await api.post<RadarResponse>('/api/process', request);
    return response.data;
  },

  /**
   * Get last cached result
   */
  async getLastResult(): Promise<RadarResponse> {
    const response = await api.get<RadarResponse>('/api/last-result');
    return response.data;
  },

  /**
   * Get processing history
   */
  async getHistory(limit: number = 20, offset: number = 0): Promise<HistoryResponse> {
    const response = await api.get<HistoryResponse>('/api/history', {
      params: { limit, offset },
    });
    return response.data;
  },

  /**
   * Get specific radar run details
   */
  async getRunDetails(runId: number): Promise<RunDetailsResponse> {
    const response = await api.get<RunDetailsResponse>(`/api/history/${runId}`);
    return response.data;
  },

  /**
   * Delete old runs, keeping last N
   */
  async cleanupOldRuns(keepLastN: number = 100): Promise<{ message: string }> {
    const response = await api.delete<{ message: string }>('/api/history/cleanup', {
      params: { keep_last_n: keepLastN },
    });
    return response.data;
  },
};

// ============================================================================
// Personal News Aggregator API
// ============================================================================

export const personalApi = {
  /**
   * Scan and aggregate personalized news feed
   */
  async scanPersonalNews(request: PersonalScanRequest): Promise<PersonalFeedResponse> {
    const response = await api.post<PersonalFeedResponse>('/api/personal/scan', request);
    return response.data;
  },

  /**
   * Get user preferences
   */
  async getUserPreferences(userId: string): Promise<UserPreferences> {
    const response = await api.get<UserPreferences>(`/api/personal/preferences/${userId}`);
    return response.data;
  },

  /**
   * Save user preferences
   */
  async saveUserPreferences(preferences: UserPreferences): Promise<{ message: string; user_id: string }> {
    const response = await api.post<{ message: string; user_id: string }>('/api/personal/preferences', preferences);
    return response.data;
  },

  /**
   * Get popular RSS sources by category
   */
  async getPopularSources(): Promise<Record<string, RSSSource[]>> {
    const response = await api.get<Record<string, RSSSource[]>>('/api/personal/sources/popular');
    return response.data;
  },

  /**
   * Add RSS source
   */
  async addSource(userId: string, sourceUrl: string): Promise<{ message: string }> {
    const response = await api.post<{ message: string }>('/api/personal/sources/add', null, {
      params: { user_id: userId, source_url: sourceUrl },
    });
    return response.data;
  },

  /**
   * Remove RSS source
   */
  async removeSource(userId: string, sourceUrl: string): Promise<{ message: string }> {
    const response = await api.delete<{ message: string }>('/api/personal/sources/remove', {
      params: { user_id: userId, source_url: sourceUrl },
    });
    return response.data;
  },

  /**
   * Add keyword filter
   */
  async addKeyword(userId: string, keyword: string): Promise<{ message: string }> {
    const response = await api.post<{ message: string }>('/api/personal/keywords/add', null, {
      params: { user_id: userId, keyword },
    });
    return response.data;
  },

  /**
   * Remove keyword filter
   */
  async removeKeyword(userId: string, keyword: string): Promise<{ message: string }> {
    const response = await api.delete<{ message: string }>('/api/personal/keywords/remove', {
      params: { user_id: userId, keyword },
    });
    return response.data;
  },

  // ============================================================================
  // Interactions & Feed Storage
  // ============================================================================

  /**
   * Track user interaction with an article
   */
  async trackInteraction(interaction: InteractionRequest): Promise<{ message: string }> {
    const response = await api.post<{ message: string }>('/api/personal/interactions/track', interaction);
    return response.data;
  },

  /**
   * Mark article as read
   */
  async markAsRead(userId: string, articleId: string): Promise<{ message: string }> {
    const response = await api.post<{ message: string }>('/api/personal/feed/mark-read', null, {
      params: { user_id: userId, article_id: articleId },
    });
    return response.data;
  },

  /**
   * Toggle like status of an article
   */
  async toggleLike(userId: string, articleId: string, liked: boolean): Promise<{ message: string }> {
    const response = await api.post<{ message: string }>('/api/personal/feed/toggle-like', null, {
      params: { user_id: userId, article_id: articleId, liked },
    });
    return response.data;
  },

  /**
   * Toggle dislike status of an article
   */
  async toggleDislike(userId: string, articleId: string, disliked: boolean): Promise<{ message: string }> {
    const response = await api.post<{ message: string }>('/api/personal/feed/toggle-dislike', null, {
      params: { user_id: userId, article_id: articleId, disliked },
    });
    return response.data;
  },

  /**
   * Toggle save status of an article
   */
  async toggleSave(userId: string, articleId: string, saved: boolean): Promise<{ message: string }> {
    const response = await api.post<{ message: string }>('/api/personal/feed/toggle-save', null, {
      params: { user_id: userId, article_id: articleId, saved },
    });
    return response.data;
  },

  /**
   * Get user's persisted feed from database
   */
  async getUserFeed(
    userId: string,
    options?: {
      limit?: number;
      offset?: number;
      unread_only?: boolean;
      saved_only?: boolean;
      liked_only?: boolean;
    }
  ): Promise<{ items: FeedItem[]; count: number }> {
    const response = await api.get<{ items: FeedItem[]; count: number }>('/api/personal/feed/get', {
      params: {
        user_id: userId,
        ...options,
      },
    });
    return response.data;
  },

  /**
   * Get user statistics
   */
  async getUserStats(userId: string, days: number = 7): Promise<UserStats> {
    const response = await api.get<UserStats>(`/api/personal/stats/${userId}`, {
      params: { days },
    });
    return response.data;
  },

  // ============================================================================
  // Onboarding
  // ============================================================================

  /**
   * Get onboarding presets
   */
  async getOnboardingPresets(): Promise<OnboardingPreset[]> {
    const response = await api.get<OnboardingPreset[]>('/api/onboarding/presets');
    return response.data;
  },

  /**
   * Complete onboarding
   */
  async completeOnboarding(request: OnboardingCompleteRequest): Promise<{ message: string; user_id: string }> {
    const response = await api.post<{ message: string; user_id: string }>('/api/onboarding/complete', request);
    return response.data;
  },

  /**
   * Get onboarding status for user
   */
  async getOnboardingStatus(userId: string): Promise<OnboardingStatus> {
    const response = await api.get<OnboardingStatus>(`/api/onboarding/status/${userId}`);
    return response.data;
  },

  // ============================================================================
  // Smart Feed & Learning Engine
  // ============================================================================

  /**
   * Get user's smart feed with caching and auto-updates
   */
  async getSmartFeed(
    userId: string,
    options?: {
      force_refresh?: boolean;
      use_cache?: boolean;
    }
  ): Promise<PersonalFeedResponse> {
    const response = await api.get<PersonalFeedResponse>('/api/personal/feed/smart', {
      params: {
        user_id: userId,
        ...options,
      },
    });
    return response.data;
  },

  /**
   * Update keyword weights for user (manually trigger ML learning)
   */
  async updateKeywordWeights(userId: string, daysBack: number = 30): Promise<UpdateWeightsResponse> {
    const response = await api.post<UpdateWeightsResponse>('/api/personal/learning/update-weights', null, {
      params: { user_id: userId, days_back: daysBack },
    });
    return response.data;
  },

  /**
   * Get current keyword weights for user
   */
  async getKeywordWeights(userId: string): Promise<KeywordWeightsResponse> {
    const response = await api.get<KeywordWeightsResponse>(`/api/personal/learning/weights/${userId}`);
    return response.data;
  },

  /**
   * Get learning insights (what the system has learned about user)
   */
  async getLearningInsights(userId: string): Promise<LearningInsights> {
    const response = await api.get<LearningInsights>(`/api/personal/learning/insights/${userId}`);
    return response.data;
  },

  /**
   * Discover new interests for user
   */
  async discoverInterests(
    userId: string,
    options?: {
      min_engagement?: number;
      limit?: number;
    }
  ): Promise<DiscoverInterestsResponse> {
    const response = await api.get<DiscoverInterestsResponse>(`/api/personal/learning/discover/${userId}`, {
      params: options,
    });
    return response.data;
  },

  // ============================================================================
  // Feed Updates & Refresh
  // ============================================================================

  /**
   * Get count of new unread items since last check
   */
  async getNewItemsCount(userId: string): Promise<NewItemsCountResponse> {
    const response = await api.get<NewItemsCountResponse>('/api/personal/feed/new-count', {
      params: { user_id: userId },
    });
    return response.data;
  },

  /**
   * Get feed metadata (counts, last update, etc.)
   */
  async getFeedMetadata(userId: string): Promise<FeedMetadata> {
    const response = await api.get<FeedMetadata>('/api/personal/feed/metadata', {
      params: { user_id: userId },
    });
    return response.data;
  },

  /**
   * Perform incremental feed refresh (fast, only new items)
   */
  async refreshFeed(userId: string): Promise<RefreshFeedResponse> {
    const response = await api.post<RefreshFeedResponse>('/api/personal/feed/refresh', null, {
      params: { user_id: userId },
    });
    return response.data;
  },

  /**
   * Mark feed as checked (updates last check timestamp)
   */
  async markFeedChecked(userId: string): Promise<{ message: string; checked_at: string }> {
    const response = await api.post<{ message: string; checked_at: string }>(
      '/api/personal/feed/mark-checked',
      null,
      { params: { user_id: userId } }
    );
    return response.data;
  },
};

// ============================================================================
// Admin API (Background Worker Control)
// ============================================================================

export const adminApi = {
  /**
   * Get background worker status
   */
  async getWorkerStatus(): Promise<WorkerStatusResponse> {
    const response = await api.get<WorkerStatusResponse>('/api/admin/worker/status');
    return response.data;
  },

  /**
   * Manually trigger a background job
   */
  async runBackgroundJob(jobId: 'update_feeds' | 'train_models' | 'discover_interests' | 'cleanup_data'): Promise<JobExecutionResponse> {
    const response = await api.post<JobExecutionResponse>('/api/admin/worker/run-job', null, {
      params: { job_id: jobId },
    });
    return response.data;
  },
};

