'use client';

import { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Newspaper, Settings, Plus, X, Search, Clock, ExternalLink, ArrowLeft, 
  Sparkles, Heart, ThumbsDown, Bookmark, Eye, TrendingUp, BarChart3, Filter, Layers
} from 'lucide-react';
import Link from 'next/link';
import { personalApi } from '@/lib/api';
import { logger } from '@/lib/logger';
import type { 
  PersonalFeedResponse, UserPreferences, RSSSource, 
  FeedItem, UserStats, OnboardingStatus 
} from '@/lib/types';

export default function PersonalNewsPage() {
  const [feed, setFeed] = useState<PersonalFeedResponse | null>(null);
  const [persistedFeed, setPersistedFeed] = useState<FeedItem[]>([]);
  const [preferences, setPreferences] = useState<UserPreferences | null>(null);
  const [stats, setStats] = useState<UserStats | null>(null);
  const [popularSources, setPopularSources] = useState<Record<string, RSSSource[]>>({});
  const [onboardingStatus, setOnboardingStatus] = useState<OnboardingStatus | null>(null);
  
  const [isLoading, setIsLoading] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showSettings, setShowSettings] = useState(false);
  const [showStats, setShowStats] = useState(false);
  const [showAddSource, setShowAddSource] = useState(false);
  const [newSourceUrl, setNewSourceUrl] = useState('');
  const [newKeyword, setNewKeyword] = useState('');
  
  const [viewMode, setViewMode] = useState<'new' | 'persisted'>('persisted');
  const [filterMode, setFilterMode] = useState<'all' | 'unread' | 'liked' | 'saved'>('all');
  const [compactView, setCompactView] = useState(false);
  const [updateFrequency, setUpdateFrequency] = useState(60);
  
  const [userId] = useState('default');
  
  // New states for UX improvements
  const [newItemsCount, setNewItemsCount] = useState(0);
  const [showNewItemsBanner, setShowNewItemsBanner] = useState(false);
  const [lastCheckTime, setLastCheckTime] = useState<Date>(new Date());
  const [feedMetadata, setFeedMetadata] = useState<any>(null);
  const [isPulling, setIsPulling] = useState(false);
  const [pullDistance, setPullDistance] = useState(0);

  // Helper function to estimate reading time
  const estimateReadingTime = (text: string): number => {
    const words = text.split(/\s+/).length;
    return Math.ceil(words / 200); // Average reading speed: 200 words/min
  };

  // Helper function to get priority badge
  const getPriorityLevel = (score: number): { level: string; color: string } => {
    if (score > 0.8) return { level: 'Высокий', color: 'bg-rose-500/20 text-rose-300 border-rose-500/40' };
    if (score > 0.6) return { level: 'Средний', color: 'bg-amber-500/20 text-amber-300 border-amber-500/40' };
    if (score > 0.4) return { level: 'Обычный', color: 'bg-blue-500/20 text-blue-300 border-blue-500/40' };
    return { level: 'Низкий', color: 'bg-slate-500/20 text-slate-400 border-slate-500/40' };
  };

  // Check for new items
  const checkForNewItems = async () => {
    try {
      const result = await personalApi.getNewItemsCount(userId);
      setNewItemsCount(result.new_items_count);
      
      if (result.new_items_count > 0 && !showNewItemsBanner) {
        setShowNewItemsBanner(true);
        logger.info('New items detected', { count: result.new_items_count });
      }
    } catch (err) {
      logger.error('Error checking for new items', err);
    }
  };

  // Load feed metadata
  const loadFeedMetadata = async () => {
    try {
      const metadata = await personalApi.getFeedMetadata(userId);
      setFeedMetadata(metadata);
    } catch (err) {
      logger.error('Error loading feed metadata', err);
    }
  };

  // Incremental refresh (fast update)
  const handleIncrementalRefresh = async () => {
    setIsRefreshing(true);
    logger.userAction('Incremental refresh initiated');

    try {
      const result = await personalApi.refreshFeed(userId);
      logger.info('Incremental refresh successful', { 
        newItems: result.new_items_added,
        totalItems: result.total_items 
      });

      // Reload persisted feed
      await loadPersistedFeed();
      await loadStats();
      await loadFeedMetadata();
      
      // Reset new items banner
      setShowNewItemsBanner(false);
      setNewItemsCount(0);
      setLastCheckTime(new Date());
      
      // Mark feed as checked
      await personalApi.markFeedChecked(userId);
      
      return result.new_items_added;
    } catch (err: any) {
      logger.error('Error in incremental refresh', err);
      throw err;
    } finally {
      setIsRefreshing(false);
    }
  };

  useEffect(() => {
    logger.info('Personal news page initialized');
    checkOnboardingStatus();
    loadPreferences();
    loadPopularSources();
    loadStats();
    loadPersistedFeed();
    loadFeedMetadata();
    
    // Initial check for new items
    checkForNewItems();
  }, []);

  // Polling for new items (every 2 minutes)
  useEffect(() => {
    const pollingInterval = setInterval(() => {
      if (!isLoading && !isRefreshing) {
        checkForNewItems();
      }
    }, 2 * 60 * 1000); // 2 minutes

    return () => clearInterval(pollingInterval);
  }, [isLoading, isRefreshing]);

  const checkOnboardingStatus = async () => {
    try {
      const status = await personalApi.getOnboardingStatus(userId);
      setOnboardingStatus(status);
      logger.debug('Onboarding status loaded', { status });
    } catch (err) {
      logger.error('Error checking onboarding', err);
    }
  };

  const loadPreferences = async () => {
    try {
      const prefs = await personalApi.getUserPreferences(userId);
      setPreferences(prefs);
      logger.debug('User preferences loaded', { sourceCount: prefs.sources.length, keywordCount: prefs.keywords.length });
    } catch (err) {
      logger.error('Error loading preferences', err);
    }
  };

  const loadPopularSources = async () => {
    try {
      const sources = await personalApi.getPopularSources();
      setPopularSources(sources);
    } catch (err) {
      console.error('Error loading popular sources:', err);
    }
  };

  const loadStats = async () => {
    try {
      const userStats = await personalApi.getUserStats(userId, 7);
      setStats(userStats);
    } catch (err) {
      console.error('Error loading stats:', err);
    }
  };

  const loadPersistedFeed = async () => {
    try {
      const options: any = { limit: 20 };
      
      if (filterMode === 'unread') options.unread_only = true;
      if (filterMode === 'liked') options.liked_only = true;
      if (filterMode === 'saved') options.saved_only = true;
      
      const result = await personalApi.getUserFeed(userId, options);
      setPersistedFeed(result.items);
    } catch (err) {
      console.error('Error loading persisted feed:', err);
    }
  };

  useEffect(() => {
    if (viewMode === 'persisted') {
      loadPersistedFeed();
    }
  }, [filterMode, viewMode]);

  const handleScan = async () => {
    setIsLoading(true);
    setError(null);
    logger.userAction('Scan news initiated');
    const startTime = performance.now();

    try {
      const result = await personalApi.scanPersonalNews({
        user_id: userId,
        time_window_hours: 24,
      });
      setFeed(result);
      setViewMode('new');
      
      const duration = performance.now() - startTime;
      logger.performance('News scan completed', duration);
      logger.info('News scan successful', { itemsFound: result.items.length });
      
      // Reload persisted feed and stats
      await loadPersistedFeed();
      await loadStats();
      await loadFeedMetadata();
    } catch (err: any) {
      setError(err.message || 'Не удалось загрузить новости');
      logger.error('Error scanning news', err);
    } finally {
      setIsLoading(false);
    }
  };

  // Pull-to-refresh handlers
  const [touchStart, setTouchStart] = useState(0);
  
  const handleTouchStart = (e: React.TouchEvent) => {
    setTouchStart(e.touches[0].clientY);
  };
  
  const handleTouchMove = (e: React.TouchEvent) => {
    const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
    
    // Only trigger pull-to-refresh at top of page
    if (scrollTop === 0 && !isRefreshing && !isLoading) {
      const touchCurrent = e.touches[0].clientY;
      const pullDist = Math.max(0, touchCurrent - touchStart);
      
      if (pullDist > 10) {
        setIsPulling(true);
        setPullDistance(Math.min(pullDist, 120));
      }
    }
  };
  
  const handleTouchEnd = async () => {
    if (isPulling && pullDistance > 80) {
      // Trigger refresh
      await handleIncrementalRefresh();
    }
    
    setIsPulling(false);
    setPullDistance(0);
  };

  const handleAddSource = async (url: string) => {
    try {
      await personalApi.addSource(userId, url);
      await loadPreferences();
      setNewSourceUrl('');
      setShowAddSource(false);
    } catch (err) {
      console.error('Error adding source:', err);
    }
  };

  const handleRemoveSource = async (url: string) => {
    try {
      await personalApi.removeSource(userId, url);
      await loadPreferences();
    } catch (err) {
      console.error('Error removing source:', err);
    }
  };

  const handleAddKeyword = async () => {
    if (!newKeyword.trim()) return;
    
    try {
      await personalApi.addKeyword(userId, newKeyword.trim());
      await loadPreferences();
      setNewKeyword('');
    } catch (err) {
      console.error('Error adding keyword:', err);
    }
  };

  const handleRemoveKeyword = async (keyword: string) => {
    try {
      await personalApi.removeKeyword(userId, keyword);
      await loadPreferences();
    } catch (err) {
      console.error('Error removing keyword:', err);
    }
  };

  const handleLike = async (articleId: string, currentlyLiked: boolean) => {
    try {
      await personalApi.toggleLike(userId, articleId, !currentlyLiked);
      await loadPersistedFeed();
      await loadStats();
    } catch (err) {
      console.error('Error toggling like:', err);
    }
  };

  const handleDislike = async (articleId: string, currentlyDisliked: boolean) => {
    try {
      await personalApi.toggleDislike(userId, articleId, !currentlyDisliked);
      await loadPersistedFeed();
    } catch (err) {
      console.error('Error toggling dislike:', err);
    }
  };

  const handleSave = async (articleId: string, currentlySaved: boolean) => {
    try {
      await personalApi.toggleSave(userId, articleId, !currentlySaved);
      await loadPersistedFeed();
      await loadStats();
    } catch (err) {
      console.error('Error toggling save:', err);
    }
  };

  const handleMarkRead = async (articleId: string) => {
    try {
      await personalApi.markAsRead(userId, articleId);
      await loadPersistedFeed();
      await loadStats();
    } catch (err) {
      console.error('Error marking as read:', err);
    }
  };

  const handleArticleClick = (articleId: string) => {
    // Track view interaction
    personalApi.trackInteraction({
      user_id: userId,
      article_id: articleId,
      interaction_type: 'click',
      clicked_read_more: true,
    }).catch(console.error);
    
    // Mark as read
    handleMarkRead(articleId);
  };

  return (
    <div 
      className="min-h-screen bg-gradient-to-br from-purple-900 via-slate-900 to-indigo-900"
      onTouchStart={handleTouchStart}
      onTouchMove={handleTouchMove}
      onTouchEnd={handleTouchEnd}
    >
      {/* Pull-to-refresh indicator */}
      <AnimatePresence>
        {isPulling && (
          <motion.div
            initial={{ opacity: 0, y: -50 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -50 }}
            className="fixed left-1/2 top-4 z-50 -translate-x-1/2 px-4"
            style={{ transform: `translateX(-50%) translateY(${pullDistance / 4}px)` }}
          >
            <div className="flex items-center gap-2 rounded-full border border-purple-500/40 bg-purple-500/10 px-3 sm:px-4 py-2 text-xs sm:text-sm text-purple-300 backdrop-blur-xl">
              <div className={`h-3.5 w-3.5 sm:h-4 sm:w-4 rounded-full border-2 border-purple-500 ${pullDistance > 80 ? 'border-t-transparent animate-spin' : ''}`} />
              <span className="whitespace-nowrap">{pullDistance > 80 ? 'Отпустите' : 'Потяните'}</span>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* New items banner */}
      <AnimatePresence>
        {showNewItemsBanner && newItemsCount > 0 && (
          <motion.div
            initial={{ opacity: 0, y: -100 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -100 }}
            className="fixed left-1/2 top-16 sm:top-20 z-50 -translate-x-1/2 px-4 w-full max-w-md"
          >
            <button
              onClick={async () => {
                await handleIncrementalRefresh();
              }}
              className="group flex items-center justify-center gap-2 sm:gap-3 w-full rounded-full border border-emerald-500/40 bg-emerald-500/10 px-4 sm:px-6 py-2.5 sm:py-3 text-xs sm:text-sm font-semibold text-emerald-300 shadow-xl shadow-emerald-500/20 backdrop-blur-xl transition-all hover:border-emerald-500/60 hover:bg-emerald-500/20"
            >
              <div className="relative">
                <Sparkles className="h-4 w-4 sm:h-5 sm:w-5" />
                <span className="absolute -right-1 -top-1 flex h-3.5 w-3.5 sm:h-4 sm:w-4 items-center justify-center rounded-full bg-emerald-500 text-[9px] sm:text-[10px] font-bold text-white">
                  {newItemsCount}
                </span>
              </div>
              <span className="truncate">Новые статьи! Нажмите для загрузки</span>
            </button>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Header */}
      <header className="sticky top-0 z-40 border-b border-white/10 bg-slate-900/90 backdrop-blur-xl">
        <div className="mx-auto max-w-7xl px-4 py-4 sm:px-6">
          {/* Mobile Header */}
          <div className="flex items-center justify-between lg:hidden">
            <div className="flex items-center gap-3">
              <Link href="/" className="group flex h-9 w-9 items-center justify-center rounded-lg border border-white/10 bg-white/5 transition-all hover:border-purple-500/40 hover:bg-white/10">
                <ArrowLeft className="h-4 w-4 text-slate-400 transition-colors group-hover:text-slate-200" />
              </Link>
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-purple-400 to-pink-500 shadow-lg shadow-purple-500/25">
                <Newspaper className="h-5 w-5 text-white" />
              </div>
              <div>
                <h1 className="text-sm font-semibold tracking-tight text-slate-100">Персональная лента</h1>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setShowStats(!showStats)}
                className={`flex h-10 w-10 items-center justify-center rounded-lg border transition-all ${
                  showStats 
                    ? 'border-purple-500/40 bg-purple-500/10 text-purple-300' 
                    : 'border-white/10 bg-white/5 text-slate-400'
                }`}
              >
                <BarChart3 className="h-4 w-4" />
              </button>
              <button
                onClick={() => setShowSettings(!showSettings)}
                className={`flex h-10 w-10 items-center justify-center rounded-lg border transition-all ${
                  showSettings 
                    ? 'border-purple-500/40 bg-purple-500/10 text-purple-300' 
                    : 'border-white/10 bg-white/5 text-slate-400'
                }`}
              >
                <Settings className="h-4 w-4" />
              </button>
            </div>
          </div>

          {/* Desktop Header */}
          <div className="hidden lg:flex lg:items-center lg:justify-between">
            <div className="flex items-center gap-4">
              <Link href="/" className="group flex h-9 w-9 items-center justify-center rounded-lg border border-white/10 bg-white/5 transition-all hover:border-purple-500/40 hover:bg-white/10">
                <ArrowLeft className="h-4 w-4 text-slate-400 transition-colors group-hover:text-slate-200" />
              </Link>
              <div className="flex items-center gap-3">
                <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-gradient-to-br from-purple-400 to-pink-500 shadow-lg shadow-purple-500/25">
                  <Newspaper className="h-5 w-5 text-white" />
                </div>
                <div>
                  <h1 className="text-base font-semibold tracking-tight text-slate-100">Персональный агрегатор</h1>
                  <p className="text-xs text-slate-500">Умная лента новостей</p>
                </div>
              </div>
            </div>

            <div className="flex items-center gap-2">
              {onboardingStatus && !onboardingStatus.onboarding_completed && (
                <Link
                  href="/onboarding"
                  className="flex items-center gap-2 rounded-lg bg-gradient-to-r from-purple-500 to-pink-500 px-4 py-2.5 text-sm font-semibold text-white shadow-lg shadow-purple-500/25 transition-all hover:from-purple-600 hover:to-pink-600 hover:shadow-purple-500/30"
                >
                  <Sparkles className="h-4 w-4" />
                  Начать онбординг
                </Link>
              )}
              <button
                onClick={() => setShowStats(!showStats)}
                className={`flex items-center gap-2 rounded-lg border px-4 py-2.5 text-sm font-medium transition-all ${
                  showStats 
                    ? 'border-purple-500/40 bg-purple-500/10 text-purple-300' 
                    : 'border-white/10 bg-white/5 text-slate-400 hover:border-white/20 hover:bg-white/10 hover:text-slate-300'
                }`}
              >
                <BarChart3 className="h-4 w-4" />
                <span>Статистика</span>
              </button>
              <button
                onClick={() => setShowSettings(!showSettings)}
                className={`flex items-center gap-2 rounded-lg border px-4 py-2.5 text-sm font-medium transition-all ${
                  showSettings 
                    ? 'border-purple-500/40 bg-purple-500/10 text-purple-300' 
                    : 'border-white/10 bg-white/5 text-slate-400 hover:border-white/20 hover:bg-white/10 hover:text-slate-300'
                }`}
              >
                <Settings className="h-4 w-4" />
                <span>Настройки</span>
              </button>
              <button
                onClick={handleIncrementalRefresh}
                disabled={isRefreshing || isLoading}
                className="group relative flex items-center gap-2 rounded-lg bg-gradient-to-r from-purple-500 to-pink-500 px-5 py-2.5 text-sm font-semibold text-white shadow-lg shadow-purple-500/25 transition-all hover:from-purple-600 hover:to-pink-600 hover:shadow-purple-500/30 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {newItemsCount > 0 && !showNewItemsBanner && (
                  <span className="absolute -right-1 -top-1 flex h-5 w-5 items-center justify-center rounded-full bg-emerald-500 text-[10px] font-bold animate-pulse">
                    {newItemsCount}
                  </span>
                )}
                <TrendingUp className={`h-4 w-4 ${isRefreshing ? 'animate-bounce' : ''}`} />
                {isRefreshing ? 'Обновление...' : 'Обновить'}
              </button>
              
              <button
                onClick={handleScan}
                disabled={isLoading || isRefreshing}
                title="Полное сканирование (медленнее)"
                className="flex items-center gap-2 rounded-lg border border-white/10 bg-white/5 px-4 py-2.5 text-sm font-medium text-slate-400 transition-all hover:border-white/20 hover:bg-white/10 hover:text-slate-300 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Search className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
                Сканировать
              </button>
            </div>
          </div>

          {/* Mobile Action Buttons */}
          <div className="mt-3 flex gap-2 lg:hidden">
            <button
              onClick={handleIncrementalRefresh}
              disabled={isRefreshing || isLoading}
              className="group relative flex flex-1 items-center justify-center gap-2 rounded-lg bg-gradient-to-r from-purple-500 to-pink-500 py-3 text-sm font-semibold text-white shadow-lg shadow-purple-500/25 transition-all hover:from-purple-600 hover:to-pink-600 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {newItemsCount > 0 && !showNewItemsBanner && (
                <span className="absolute -right-1 -top-1 flex h-5 w-5 items-center justify-center rounded-full bg-emerald-500 text-[10px] font-bold animate-pulse">
                  {newItemsCount}
                </span>
              )}
              <TrendingUp className={`h-4 w-4 ${isRefreshing ? 'animate-bounce' : ''}`} />
              {isRefreshing ? 'Обновление...' : 'Обновить'}
            </button>
            
            <button
              onClick={handleScan}
              disabled={isLoading || isRefreshing}
              title="Полное сканирование"
              className="flex items-center justify-center gap-2 rounded-lg border border-white/10 bg-white/5 px-4 py-3 text-sm font-medium text-slate-400 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Search className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
            </button>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-4 py-4 sm:py-6 md:py-8">
        {/* Stats Panel */}
        <AnimatePresence>
          {showStats && stats && (
            <motion.div
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
              className="mb-6 overflow-hidden rounded-xl border border-white/10 bg-gradient-to-br from-white/5 to-white/[0.02] backdrop-blur"
            >
              <div className="border-b border-white/10 px-6 py-4">
                <div className="flex items-center justify-between">
                  <h2 className="text-lg font-semibold text-slate-100">Ваша активность</h2>
                  <span className="text-xs text-slate-500">Последние 7 дней</span>
                </div>
              </div>
              <div className="p-4 sm:p-6">
                <div className="grid gap-3 grid-cols-2 sm:gap-4 md:grid-cols-4">
                  <div className="group relative overflow-hidden rounded-xl border border-white/10 bg-white/5 p-4 sm:p-5 transition-all hover:border-purple-500/30 hover:bg-white/10">
                    <div className="absolute right-0 top-0 h-20 w-20 -translate-y-10 translate-x-10 rounded-full bg-purple-500/10 blur-2xl transition-transform group-hover:scale-150" />
                    <div className="relative">
                      <div className="mb-1 sm:mb-2 text-2xl sm:text-3xl font-bold text-purple-400">{stats.total_articles_in_feed}</div>
                      <div className="text-xs sm:text-sm font-medium text-slate-400">Статей в ленте</div>
                    </div>
                  </div>
                  <div className="group relative overflow-hidden rounded-xl border border-white/10 bg-white/5 p-4 sm:p-5 transition-all hover:border-blue-500/30 hover:bg-white/10">
                    <div className="absolute right-0 top-0 h-20 w-20 -translate-y-10 translate-x-10 rounded-full bg-blue-500/10 blur-2xl transition-transform group-hover:scale-150" />
                    <div className="relative">
                      <div className="mb-1 sm:mb-2 text-2xl sm:text-3xl font-bold text-blue-400">{stats.articles_read}</div>
                      <div className="text-xs sm:text-sm font-medium text-slate-400">Прочитано</div>
                    </div>
                  </div>
                  <div className="group relative overflow-hidden rounded-xl border border-white/10 bg-white/5 p-4 sm:p-5 transition-all hover:border-pink-500/30 hover:bg-white/10">
                    <div className="absolute right-0 top-0 h-20 w-20 -translate-y-10 translate-x-10 rounded-full bg-pink-500/10 blur-2xl transition-transform group-hover:scale-150" />
                    <div className="relative">
                      <div className="mb-1 sm:mb-2 text-2xl sm:text-3xl font-bold text-pink-400">{stats.articles_liked}</div>
                      <div className="text-xs sm:text-sm font-medium text-slate-400">Понравилось</div>
                    </div>
                  </div>
                  <div className="group relative overflow-hidden rounded-xl border border-white/10 bg-white/5 p-4 sm:p-5 transition-all hover:border-amber-500/30 hover:bg-white/10">
                    <div className="absolute right-0 top-0 h-20 w-20 -translate-y-10 translate-x-10 rounded-full bg-amber-500/10 blur-2xl transition-transform group-hover:scale-150" />
                    <div className="relative">
                      <div className="mb-1 sm:mb-2 text-2xl sm:text-3xl font-bold text-amber-400">{stats.articles_saved}</div>
                      <div className="text-xs sm:text-sm font-medium text-slate-400">Сохранено</div>
                    </div>
                  </div>
                </div>
                <div className="mt-3 sm:mt-4 flex flex-col sm:flex-row items-center justify-between gap-2 rounded-xl border border-white/10 bg-white/5 px-4 sm:px-5 py-3 sm:py-4">
                  <span className="text-xs sm:text-sm font-medium text-slate-400">Среднее время чтения</span>
                  <span className="text-xl sm:text-2xl font-bold text-emerald-400">{Math.round(stats.avg_view_duration_seconds)}с</span>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Settings Panel */}
        <AnimatePresence>
          {showSettings && preferences && (
            <motion.div
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="mb-6 sm:mb-8 rounded-2xl border border-white/10 bg-slate-800/50 p-4 sm:p-6 backdrop-blur"
            >
              <h2 className="mb-4 sm:mb-6 text-lg sm:text-xl font-semibold text-slate-100">Настройки ленты</h2>

              {/* Sources */}
              <div className="mb-6">
                <div className="mb-3 flex items-center justify-between">
                  <h3 className="text-sm font-semibold uppercase tracking-wider text-slate-300">
                    RSS Источники ({preferences.sources.length})
                  </h3>
                  <button
                    onClick={() => setShowAddSource(!showAddSource)}
                    className="flex items-center gap-1 text-xs text-purple-400 hover:text-purple-300"
                  >
                    <Plus className="h-4 w-4" />
                    Добавить
                  </button>
                </div>

                {showAddSource && (
                  <div className="mb-4 flex gap-2">
                    <input
                      type="url"
                      value={newSourceUrl}
                      onChange={(e) => setNewSourceUrl(e.target.value)}
                      placeholder="https://example.com/rss"
                      className="flex-1 rounded-lg border border-white/10 bg-white/5 px-4 py-2 text-sm text-slate-100 placeholder-slate-500 focus:border-purple-500/40 focus:outline-none"
                    />
                    <button
                      onClick={() => handleAddSource(newSourceUrl)}
                      className="rounded-lg bg-purple-500 px-4 py-2 text-sm font-semibold text-white hover:bg-purple-600"
                    >
                      Добавить
                    </button>
                  </div>
                )}

                <div className="max-h-60 space-y-2 overflow-y-auto">
                  {preferences.sources.map((source) => (
                    <div
                      key={source}
                      className="flex items-center gap-2 rounded-lg border border-white/10 bg-white/5 px-3 sm:px-4 py-2"
                    >
                      <span className="truncate text-xs sm:text-sm text-slate-300 flex-1 min-w-0">{source}</span>
                      <button
                        onClick={() => handleRemoveSource(source)}
                        className="flex-shrink-0 text-slate-400 hover:text-rose-400 p-1"
                      >
                        <X className="h-4 w-4" />
                      </button>
                    </div>
                  ))}
                </div>
              </div>

              {/* Keywords */}
              <div className="mb-6">
                <h3 className="mb-3 text-sm font-semibold uppercase tracking-wider text-slate-300">
                  Ключевые слова
                </h3>
                <div className="mb-3 flex gap-2">
                  <input
                    type="text"
                    value={newKeyword}
                    onChange={(e) => setNewKeyword(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleAddKeyword()}
                    placeholder="Добавить ключевое слово"
                    className="flex-1 rounded-lg border border-white/10 bg-white/5 px-4 py-2 text-sm text-slate-100 placeholder-slate-500 focus:border-purple-500/40 focus:outline-none"
                  />
                  <button
                    onClick={handleAddKeyword}
                    className="rounded-lg bg-purple-500 px-4 py-2 text-sm font-semibold text-white hover:bg-purple-600"
                  >
                    Добавить
                  </button>
                </div>
                <div className="flex flex-wrap gap-2">
                  {preferences.keywords.map((keyword) => (
                    <div
                      key={keyword}
                      className="flex items-center gap-2 rounded-full bg-purple-500/20 px-3 py-1 text-sm text-purple-300"
                    >
                      {keyword}
                      <button onClick={() => handleRemoveKeyword(keyword)} className="hover:text-purple-100">
                        <X className="h-3 w-3" />
                      </button>
                    </div>
                  ))}
                </div>
              </div>

              {/* Update Frequency */}
              <div>
                <h3 className="mb-3 text-sm font-semibold uppercase tracking-wider text-slate-300">
                  Частота обновлений
                </h3>
                <select
                  value={preferences.update_frequency_minutes}
                  onChange={async (e) => {
                    const newFreq = parseInt(e.target.value);
                    const updated = { ...preferences, update_frequency_minutes: newFreq };
                    await personalApi.saveUserPreferences(updated);
                    await loadPreferences();
                  }}
                  className="w-full rounded-lg border border-white/10 bg-white/5 px-4 py-2 text-sm text-slate-100 focus:border-purple-500/40 focus:outline-none"
                >
                  <option value={15}>Каждые 15 минут ⚡</option>
                  <option value={30}>Каждые 30 минут</option>
                  <option value={60}>Каждый час</option>
                  <option value={180}>Каждые 3 часа</option>
                  <option value={360}>Каждые 6 часов</option>
                  <option value={1440}>Раз в день</option>
                </select>
                <p className="mt-2 text-xs text-slate-400">
                  Автоматическое обновление ленты в фоновом режиме
                </p>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* View Controls */}
        <div className="mb-6 rounded-xl border border-white/10 bg-white/5 p-3 sm:p-4 backdrop-blur">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            {/* View Mode Switcher */}
            <div className="flex justify-center sm:justify-start">
              <div className="flex gap-1 rounded-lg bg-white/5 p-1 w-full sm:w-auto">
                <button
                  onClick={() => setViewMode('persisted')}
                  className={`flex-1 sm:flex-none rounded-lg px-3 sm:px-4 py-2 text-xs sm:text-sm font-medium transition-all ${
                    viewMode === 'persisted'
                      ? 'bg-purple-500 text-white shadow-lg shadow-purple-500/25'
                      : 'text-slate-400 hover:text-slate-300'
                  }`}
                >
                  Моя лента
                </button>
                <button
                  onClick={() => setViewMode('new')}
                  className={`flex-1 sm:flex-none rounded-lg px-3 sm:px-4 py-2 text-xs sm:text-sm font-medium transition-all ${
                    viewMode === 'new'
                      ? 'bg-purple-500 text-white shadow-lg shadow-purple-500/25'
                      : 'text-slate-400 hover:text-slate-300'
                  }`}
                >
                  Новое
                </button>
              </div>
            </div>

            {/* Filters and View Toggle */}
            <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2 sm:gap-2">
              {viewMode === 'persisted' && (
                <div className="flex items-center gap-2 overflow-x-auto pb-1 sm:pb-0">
                  <Filter className="hidden sm:block h-4 w-4 text-slate-500 flex-shrink-0" />
                  <div className="flex gap-1 rounded-lg bg-white/5 p-1 min-w-0">
                    {[
                      { key: 'all', label: 'Все' },
                      { key: 'unread', label: 'Непрочитанные' },
                      { key: 'liked', label: '❤️' },
                      { key: 'saved', label: '🔖' }
                    ].map((mode) => (
                      <button
                        key={mode.key}
                        onClick={() => setFilterMode(mode.key as any)}
                        className={`flex-shrink-0 rounded-md px-2 sm:px-3 py-1.5 text-xs font-medium transition-all whitespace-nowrap ${
                          filterMode === mode.key
                            ? 'bg-pink-500 text-white shadow-sm'
                            : 'text-slate-400 hover:text-slate-300'
                        }`}
                        title={mode.key === 'liked' ? 'Избранное' : mode.key === 'saved' ? 'Сохранённые' : mode.label}
                      >
                        {mode.label}
                      </button>
                    ))}
                  </div>
                </div>
              )}
              <button
                onClick={() => setCompactView(!compactView)}
                className="rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-xs font-medium text-slate-400 transition-all hover:border-white/20 hover:text-slate-300 whitespace-nowrap"
              >
                {compactView ? '📋 Детальный' : '📝 Компактный'}
              </button>
            </div>
          </div>
        </div>

        {/* Error */}
        {error && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="mb-8 rounded-2xl border border-rose-500/40 bg-rose-950/60 p-6 text-rose-200"
          >
            {error}
          </motion.div>
        )}

        {/* Loading */}
        {isLoading && (
          <div className="flex items-center justify-center py-20">
            <div className="text-center">
              <div className="mx-auto mb-4 h-12 w-12 animate-spin rounded-full border-4 border-purple-500/20 border-t-purple-500" />
              <p className="text-slate-400">Сканирование новостей...</p>
            </div>
          </div>
        )}

        {/* News Feed - Persisted */}
        {viewMode === 'persisted' && !isLoading && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-4">
            {persistedFeed.length === 0 ? (
              <motion.div 
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className="rounded-xl sm:rounded-2xl border border-white/10 bg-gradient-to-br from-white/5 to-white/[0.02] p-6 sm:p-12 text-center backdrop-blur"
              >
                <div className="mx-auto mb-4 sm:mb-6 flex h-16 w-16 sm:h-20 sm:w-20 items-center justify-center rounded-full bg-gradient-to-br from-purple-500/20 to-pink-500/20">
                  <Newspaper className="h-8 w-8 sm:h-10 sm:w-10 text-purple-400" />
                </div>
                <h3 className="mb-2 sm:mb-3 text-xl sm:text-2xl font-bold text-slate-100">
                  {filterMode === 'all' && 'Ваша лента пуста'}
                  {filterMode === 'unread' && 'Всё прочитано! 🎉'}
                  {filterMode === 'liked' && 'Пока нет избранных'}
                  {filterMode === 'saved' && 'Нет сохранённых статей'}
                </h3>
                <p className="mb-4 sm:mb-6 text-sm sm:text-base text-slate-400">
                  {filterMode === 'all' && 'Нажмите "Обновить ленту" чтобы загрузить новости из ваших источников'}
                  {filterMode === 'unread' && 'Отличная работа! Вы прочитали все статьи. Новые появятся автоматически через несколько минут.'}
                  {filterMode === 'liked' && 'Отмечайте понравившиеся статьи с помощью ❤️'}
                  {filterMode === 'saved' && 'Сохраняйте важные статьи для чтения позже с помощью 🔖'}
                </p>
                
                {filterMode === 'all' && (
                  <div className="flex flex-col items-center gap-4">
                    <button
                      onClick={handleIncrementalRefresh}
                      disabled={isRefreshing}
                      className="inline-flex items-center gap-2 rounded-lg bg-gradient-to-r from-purple-500 to-pink-500 px-5 sm:px-6 py-2.5 sm:py-3 text-sm sm:text-base font-semibold text-white shadow-lg shadow-purple-500/25 transition-all hover:from-purple-600 hover:to-pink-600"
                    >
                      <TrendingUp className="h-4 w-4 sm:h-5 sm:w-5" />
                      Обновить ленту
                    </button>
                    
                    {feedMetadata && feedMetadata.last_check && (
                      <p className="text-[10px] sm:text-xs text-slate-500">
                        Последнее обновление: {new Date(feedMetadata.last_check).toLocaleString('ru-RU')}
                      </p>
                    )}
                    
                    <div className="mt-4 rounded-xl border border-blue-500/20 bg-blue-500/10 p-3 sm:p-4 text-left">
                      <p className="mb-2 text-xs sm:text-sm font-semibold text-blue-300">💡 Подсказка:</p>
                      <p className="text-xs sm:text-sm text-slate-400">
                        Настройте ваши источники и ключевые слова в настройках, чтобы получать персонализированные новости. 
                        Лента обновляется автоматически каждые {preferences?.update_frequency_minutes || 60} минут.
                      </p>
                    </div>
                  </div>
                )}
                
                {filterMode !== 'all' && (
                  <button
                    onClick={() => setFilterMode('all')}
                    className="inline-flex items-center gap-2 rounded-lg border border-white/10 bg-white/5 px-5 sm:px-6 py-2.5 sm:py-3 text-sm sm:text-base font-semibold text-slate-300 transition-all hover:border-white/20 hover:bg-white/10"
                  >
                    Показать все статьи
                  </button>
                )}
              </motion.div>
            ) : (
              persistedFeed.map((item, index) => (
                <FeedItemCard
                  key={item.id}
                  item={item}
                  index={index}
                  compact={compactView}
                  onLike={handleLike}
                  onDislike={handleDislike}
                  onSave={handleSave}
                  onArticleClick={handleArticleClick}
                />
              ))
            )}
          </motion.div>
        )}

        {/* News Feed - New Scan */}
        {viewMode === 'new' && feed && !isLoading && (
          <>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="mb-6 sm:mb-8 grid gap-3 grid-cols-2 sm:gap-4 md:grid-cols-4"
            >
              <div className="rounded-xl border border-white/10 bg-white/5 p-3 sm:p-4 backdrop-blur">
                <div className="text-2xl sm:text-3xl font-bold text-purple-400">{feed.items.length}</div>
                <div className="text-[10px] sm:text-xs text-slate-400">Новостей в ленте</div>
              </div>
              <div className="rounded-xl border border-white/10 bg-white/5 p-3 sm:p-4 backdrop-blur">
                <div className="text-2xl sm:text-3xl font-bold text-purple-400">{feed.total_articles_processed}</div>
                <div className="text-[10px] sm:text-xs text-slate-400">Обработано</div>
              </div>
              <div className="rounded-xl border border-white/10 bg-white/5 p-3 sm:p-4 backdrop-blur">
                <div className="text-2xl sm:text-3xl font-bold text-purple-400">{feed.filtered_count}</div>
                <div className="text-[10px] sm:text-xs text-slate-400">Отфильтровано</div>
              </div>
              <div className="rounded-xl border border-white/10 bg-white/5 p-3 sm:p-4 backdrop-blur">
                <div className="text-2xl sm:text-3xl font-bold text-purple-400">{Math.round(feed.processing_time_seconds)}s</div>
                <div className="text-[10px] sm:text-xs text-slate-400">Время обработки</div>
              </div>
            </motion.div>

            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-4">
              {feed.items.map((item, index) => {
                const readingTime = Math.ceil(item.summary.split(/\s+/).length / 200);
                const priorityIcon = item.relevance_score > 0.8 ? '🔥🔥🔥' : 
                                     item.relevance_score > 0.6 ? '🔥🔥' : 
                                     item.relevance_score > 0.4 ? '🔥' : '';
                
                return (
                  <motion.article
                    key={item.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.05 }}
                    className="group rounded-xl sm:rounded-2xl border border-white/10 bg-white/5 p-4 sm:p-6 backdrop-blur transition-all hover:border-purple-500/40 hover:bg-white/10"
                  >
                    <div className="mb-3 flex items-start justify-between gap-3 sm:gap-4">
                      <h2 className="flex-1 text-base sm:text-xl font-semibold text-slate-100 group-hover:text-purple-300 leading-snug">
                        {item.title}
                      </h2>
                      <div className="flex flex-col sm:flex-row gap-1 sm:gap-2 flex-shrink-0">
                        {priorityIcon && (
                          <div className="flex items-center justify-center rounded-full bg-orange-500/20 px-2 py-1 text-[10px] sm:text-xs">
                            {priorityIcon}
                          </div>
                        )}
                        {item.cluster_size > 1 && (
                          <div className="flex items-center gap-1 rounded-full bg-cyan-500/20 px-2 py-1 text-[10px] sm:text-xs text-cyan-300 whitespace-nowrap">
                            🔄 {item.cluster_size}
                          </div>
                        )}
                      </div>
                    </div>

                    <p className="mb-3 sm:mb-4 text-xs sm:text-sm leading-relaxed text-slate-300">{item.summary}</p>

                    <div className="flex flex-wrap items-center gap-2 sm:gap-4 text-[10px] sm:text-xs text-slate-400">
                      <div className="flex items-center gap-1">
                        <Clock className="h-3 w-3" />
                        {new Date(item.published_at).toLocaleString('ru-RU', {
                          day: 'numeric',
                          month: 'short',
                          hour: '2-digit',
                          minute: '2-digit',
                        })}
                      </div>
                      <div className="flex items-center gap-1">
                        ⏱️ {readingTime} мин
                      </div>
                      <div className="hidden sm:block truncate max-w-[150px]">Источник: {item.source}</div>
                      {item.matched_keywords && item.matched_keywords.length > 0 && (
                        <div className="flex flex-wrap gap-1">
                          {item.matched_keywords.slice(0, 2).map((kw) => (
                            <span key={kw} className="rounded bg-purple-500/20 px-1.5 sm:px-2 py-0.5 text-purple-300">
                              {kw}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>

                    <div className="mt-3 sm:mt-4 flex items-center justify-center sm:justify-between border-t border-white/10 pt-3 sm:pt-4">
                      <a
                        href={item.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        onClick={() => handleArticleClick(item.id)}
                        className="flex items-center gap-2 text-xs sm:text-sm text-purple-400 transition-colors hover:text-purple-300 font-medium"
                      >
                        Читать полностью
                        <ExternalLink className="h-3.5 w-3.5 sm:h-4 sm:w-4" />
                      </a>
                    </div>
                  </motion.article>
                );
              })}
            </motion.div>
          </>
        )}

        {/* Welcome message */}
        {!feed && !isLoading && viewMode === 'new' && persistedFeed.length === 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="rounded-xl sm:rounded-2xl border border-white/10 bg-white/5 p-6 sm:p-12 text-center backdrop-blur"
          >
            <Newspaper className="mx-auto mb-4 sm:mb-6 h-12 w-12 sm:h-16 sm:w-16 text-purple-400" />
            <h2 className="mb-3 sm:mb-4 text-xl sm:text-2xl font-semibold text-slate-100">Добро пожаловать!</h2>
            <p className="mb-4 sm:mb-6 text-sm sm:text-base text-slate-400">
              Настройте источники новостей и ключевые слова, затем нажмите &quot;Обновить ленту&quot;
            </p>
            <button
              onClick={() => setShowSettings(true)}
              className="inline-flex items-center gap-2 rounded-lg bg-purple-500 px-5 sm:px-6 py-2.5 sm:py-3 text-sm sm:text-base font-semibold text-white hover:bg-purple-600"
            >
              <Settings className="h-4 w-4 sm:h-5 sm:w-5" />
              Открыть настройки
            </button>
          </motion.div>
        )}
      </main>
    </div>
  );
}

// Feed Item Card Component
function FeedItemCard({
  item,
  index,
  compact,
  onLike,
  onDislike,
  onSave,
  onArticleClick,
}: {
  item: FeedItem;
  index: number;
  compact: boolean;
  onLike: (id: string, current: boolean) => void;
  onDislike: (id: string, current: boolean) => void;
  onSave: (id: string, current: boolean) => void;
  onArticleClick: (id: string) => void;
}) {
  // Calculate reading time
  const readingTime = Math.ceil(item.summary.split(/\s+/).length / 200);
  
  // Get priority level
  const priority = item.relevance_score > 0.8 ? { level: 'Высокий', color: 'rose' } : 
                   item.relevance_score > 0.6 ? { level: 'Средний', color: 'amber' } : 
                   item.relevance_score > 0.4 ? { level: 'Обычный', color: 'blue' } :
                   { level: '', color: 'slate' };

  return (
    <motion.article
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05, duration: 0.3 }}
      className={`group relative overflow-hidden rounded-xl sm:rounded-2xl border backdrop-blur transition-all ${
        item.is_read 
          ? 'border-white/5 bg-white/[0.02] opacity-70 hover:opacity-100' 
          : 'border-white/10 bg-white/5 hover:border-purple-500/30 hover:shadow-xl hover:shadow-purple-500/5'
      } ${compact ? 'p-3 sm:p-4' : 'p-4 sm:p-6'}`}
    >
      {/* Header with badges */}
      <div className="mb-3 sm:mb-4 flex items-start justify-between gap-3 sm:gap-4">
        <div className="flex-1 space-y-2 min-w-0">
          <div className="flex flex-wrap items-center gap-1.5 sm:gap-2">
            {priority.level && (
              <span className={`inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-[10px] sm:text-xs font-medium ${
                priority.color === 'rose' ? 'border-rose-500/40 bg-rose-500/10 text-rose-300' :
                priority.color === 'amber' ? 'border-amber-500/40 bg-amber-500/10 text-amber-300' :
                'border-blue-500/40 bg-blue-500/10 text-blue-300'
              }`}>
                <TrendingUp className="h-2.5 w-2.5 sm:h-3 sm:w-3" />
                {priority.level}
              </span>
            )}
            {item.cluster_size > 1 && (
              <span className="inline-flex items-center gap-1 rounded-full border border-cyan-500/40 bg-cyan-500/10 px-2 py-0.5 text-[10px] sm:text-xs font-medium text-cyan-300">
                <Layers className="h-2.5 w-2.5 sm:h-3 sm:w-3" />
                {item.cluster_size}
              </span>
            )}
            {item.is_read && (
              <span className="inline-flex items-center gap-1 rounded-full border border-slate-500/40 bg-slate-500/10 px-2 py-0.5 text-[10px] sm:text-xs text-slate-400">
                <Eye className="h-2.5 w-2.5 sm:h-3 sm:w-3" />
                <span className="hidden sm:inline">Прочитано</span>
              </span>
            )}
          </div>
          <h2 className={`font-semibold leading-snug text-slate-50 transition-colors group-hover:text-purple-300 ${compact ? 'text-sm sm:text-base' : 'text-base sm:text-xl'}`}>
            {item.title}
          </h2>
        </div>
        <div className="flex flex-shrink-0 gap-1">
          {item.is_liked && (
            <div className="flex h-7 w-7 sm:h-8 sm:w-8 items-center justify-center rounded-lg bg-pink-500/20">
              <Heart className="h-3.5 w-3.5 sm:h-4 sm:w-4 fill-pink-300 text-pink-300" />
            </div>
          )}
          {item.is_saved && (
            <div className="flex h-7 w-7 sm:h-8 sm:w-8 items-center justify-center rounded-lg bg-amber-500/20">
              <Bookmark className="h-3.5 w-3.5 sm:h-4 sm:w-4 fill-amber-300 text-amber-300" />
            </div>
          )}
        </div>
      </div>

      {/* Summary */}
      {!compact && (
        <p className="mb-3 sm:mb-4 text-sm sm:text-base leading-relaxed text-slate-300">{item.summary}</p>
      )}

      {/* Metadata */}
      <div className="mb-3 sm:mb-4 flex flex-wrap items-center gap-2 sm:gap-3 text-[10px] sm:text-xs text-slate-500">
        <span className="flex items-center gap-1 sm:gap-1.5">
          <Clock className="h-3 w-3 sm:h-3.5 sm:w-3.5" />
          {new Date(item.published_at).toLocaleString('ru-RU', {
            day: 'numeric',
            month: 'short',
            hour: '2-digit',
            minute: '2-digit',
          })}
        </span>
        <span className="text-slate-600">•</span>
        <span>{readingTime} мин</span>
        <span className="text-slate-600 hidden sm:inline">•</span>
        <span className="hidden sm:inline truncate max-w-[120px]">{item.source}</span>
        {item.matched_keywords.length > 0 && (
          <>
            <span className="text-slate-600 hidden sm:inline">•</span>
            <div className="flex flex-wrap gap-1 sm:gap-1.5">
              {item.matched_keywords.slice(0, 2).map((kw) => (
                <span key={kw} className="rounded-md bg-purple-500/15 px-1.5 sm:px-2 py-0.5 text-purple-300">
                  {kw}
                </span>
              ))}
            </div>
          </>
        )}
      </div>

      {/* Actions */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3 sm:justify-between border-t border-white/5 pt-3 sm:pt-4">
        <a
          href={item.url}
          target="_blank"
          rel="noopener noreferrer"
          onClick={() => onArticleClick(item.article_id)}
          className="group/link flex items-center justify-center sm:justify-start gap-2 text-xs sm:text-sm font-medium text-purple-400 transition-all hover:text-purple-300 py-2 sm:py-0"
        >
          Читать полностью
          <ExternalLink className="h-3.5 w-3.5 sm:h-4 sm:w-4 transition-transform group-hover/link:translate-x-0.5 group-hover/link:-translate-y-0.5" />
        </a>

        <div className="flex gap-2 justify-center sm:justify-end">
          <button
            onClick={() => onLike(item.article_id, item.is_liked)}
            className={`group/btn flex flex-1 sm:flex-none items-center justify-center gap-1.5 rounded-lg px-3 sm:px-3 py-2.5 sm:py-2 text-sm font-medium transition-all ${
              item.is_liked
                ? 'bg-pink-500/20 text-pink-300 hover:bg-pink-500/25'
                : 'bg-white/5 text-slate-400 hover:bg-pink-500/10 hover:text-pink-300'
            }`}
            title="Нравится"
          >
            <Heart className={`h-4 w-4 transition-transform group-hover/btn:scale-110 ${item.is_liked ? 'fill-pink-300' : ''}`} />
          </button>
          
          <button
            onClick={() => onDislike(item.article_id, item.is_disliked)}
            className={`group/btn flex flex-1 sm:flex-none items-center justify-center gap-1.5 rounded-lg px-3 sm:px-3 py-2.5 sm:py-2 text-sm font-medium transition-all ${
              item.is_disliked
                ? 'bg-slate-500/20 text-slate-300 hover:bg-slate-500/25'
                : 'bg-white/5 text-slate-400 hover:bg-slate-500/10 hover:text-slate-300'
            }`}
            title="Не нравится"
          >
            <ThumbsDown className={`h-4 w-4 transition-transform group-hover/btn:scale-110 ${item.is_disliked ? 'fill-slate-300' : ''}`} />
          </button>
          
          <button
            onClick={() => onSave(item.article_id, item.is_saved)}
            className={`group/btn flex flex-1 sm:flex-none items-center justify-center gap-1.5 rounded-lg px-3 sm:px-3 py-2.5 sm:py-2 text-sm font-medium transition-all ${
              item.is_saved
                ? 'bg-amber-500/20 text-amber-300 hover:bg-amber-500/25'
                : 'bg-white/5 text-slate-400 hover:bg-amber-500/10 hover:text-amber-300'
            }`}
            title="Сохранить"
          >
            <Bookmark className={`h-4 w-4 transition-transform group-hover/btn:scale-110 ${item.is_saved ? 'fill-amber-300' : ''}`} />
          </button>
        </div>
      </div>
    </motion.article>
  );
}