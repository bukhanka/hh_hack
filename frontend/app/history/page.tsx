'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { ArrowLeft, Clock, RefreshCw, Trash2 } from 'lucide-react';
import Link from 'next/link';
import HistoryList from '@/components/HistoryList';
import MoneyBackground from '@/components/MoneyBackground';
import { radarApi } from '@/lib/api';
import { RadarRun } from '@/lib/types';

export default function HistoryPage() {
  const router = useRouter();
  const [runs, setRuns] = useState<RadarRun[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isRefreshing, setIsRefreshing] = useState(false);

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await radarApi.getHistory(50);
      setRuns(response.history);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Не удалось загрузить историю';
      setError(errorMessage);
      console.error('Error loading history:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRefresh = async () => {
    setIsRefreshing(true);
    await loadHistory();
    setIsRefreshing(false);
  };

  const handleRunClick = async (runId: number) => {
    try {
      const details = await radarApi.getRunDetails(runId);
      
      // Store in sessionStorage to pass to main page
      sessionStorage.setItem('radarResult', JSON.stringify({
        stories: details.stories,
        total_articles_processed: details.total_articles_processed,
        time_window_hours: details.time_window_hours,
        generated_at: details.created_at,
        processing_time_seconds: details.processing_time_seconds,
      }));
      
      // Navigate to main page
      router.push('/');
    } catch (err) {
      console.error('Error loading run details:', err);
      setError('Не удалось загрузить детали запуска');
    }
  };

  const handleCleanup = async () => {
    if (!confirm('Удалить старые запуски, оставив последние 50?')) return;

    try {
      await radarApi.cleanupOldRuns(50);
      await loadHistory();
    } catch (err) {
      console.error('Error cleaning up:', err);
      setError('Не удалось выполнить очистку');
    }
  };

  return (
    <div className="relative min-h-screen overflow-hidden bg-[#05070f] text-slate-100">
      <MoneyBackground />
      
      <div className="pointer-events-none absolute inset-0 z-0">
        <div className="absolute inset-x-0 top-0 h-[520px] bg-[radial-gradient(circle_at_top,rgba(14,116,144,0.35)_0%,rgba(5,7,15,0.4)_55%,rgba(5,7,15,0)_100%)]" />
      </div>

      <header className="sticky top-0 z-40 border-b border-white/10 bg-[#05070f]/80 backdrop-blur-xl">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-4 lg:px-8">
          <Link
            href="/"
            className="flex items-center gap-2 text-sm text-slate-400 transition-colors hover:text-slate-200"
          >
            <ArrowLeft className="h-4 w-4" />
            Назад к радару
          </Link>
          
          <div className="flex items-center gap-3">
            <button
              onClick={handleRefresh}
              disabled={isRefreshing}
              className="flex items-center gap-2 rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-xs font-medium text-slate-300 transition-all hover:border-cyan-500/40 hover:bg-white/10 disabled:opacity-50"
            >
              <RefreshCw className={`h-3.5 w-3.5 ${isRefreshing ? 'animate-spin' : ''}`} />
              Обновить
            </button>
            
            <button
              onClick={handleCleanup}
              className="flex items-center gap-2 rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-xs font-medium text-slate-300 transition-all hover:border-rose-500/40 hover:bg-rose-500/10 hover:text-rose-300"
            >
              <Trash2 className="h-3.5 w-3.5" />
              Очистить
            </button>
          </div>
        </div>
      </header>

      <main className="relative mx-auto max-w-6xl px-4 pb-20 pt-12 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="mb-12"
        >
          <div className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-4 py-2 text-[0.7rem] uppercase tracking-[0.35em] text-slate-300">
            <Clock className="h-4 w-4 text-cyan-300" />
            История обработки
          </div>
          
          <h1 className="mt-6 text-4xl font-semibold text-slate-50 md:text-5xl">
            Архив запусков RADAR
          </h1>
          
          <p className="mt-4 max-w-2xl text-lg text-slate-400">
            Просматривайте результаты предыдущих сканирований новостей. 
            Нажмите на запуск для просмотра всех найденных сюжетов.
          </p>

          {runs.length > 0 && (
            <div className="mt-6 flex items-center gap-4 text-sm">
              <div className="flex items-center gap-2 text-slate-400">
                <div className="h-2 w-2 rounded-full bg-cyan-400" />
                Всего запусков: <span className="font-semibold text-slate-200">{runs.length}</span>
              </div>
              <div className="flex items-center gap-2 text-slate-400">
                <div className="h-2 w-2 rounded-full bg-blue-400" />
                Последний: <span className="font-semibold text-slate-200">
                  {new Date(runs[0]?.created_at).toLocaleString('ru-RU')}
                </span>
              </div>
            </div>
          )}
        </motion.div>

        {error && (
          <motion.div
            initial={{ opacity: 0, y: -12 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-8 rounded-2xl border border-rose-500/40 bg-rose-950/60 p-6 text-sm text-rose-200 backdrop-blur"
          >
            <p className="font-semibold">Ошибка: {error}</p>
          </motion.div>
        )}

        <HistoryList 
          runs={runs} 
          onRunClick={handleRunClick}
          isLoading={isLoading}
        />
      </main>
    </div>
  );
}

