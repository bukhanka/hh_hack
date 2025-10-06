'use client';

import { motion } from 'framer-motion';
import { Clock, FileText, TrendingUp, Zap } from 'lucide-react';
import { RadarRun } from '@/lib/types';

interface HistoryListProps {
  runs: RadarRun[];
  onRunClick: (runId: number) => void;
  isLoading?: boolean;
}

export default function HistoryList({ runs, onRunClick, isLoading }: HistoryListProps) {
  if (isLoading) {
    return (
      <div className="space-y-4">
        {[1, 2, 3].map((i) => (
          <div
            key={i}
            className="animate-pulse rounded-2xl border border-white/10 bg-white/5 p-6"
          >
            <div className="h-6 w-1/3 rounded bg-white/10" />
            <div className="mt-4 space-y-2">
              <div className="h-4 w-full rounded bg-white/10" />
              <div className="h-4 w-2/3 rounded bg-white/10" />
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (runs.length === 0) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        className="rounded-3xl border border-white/10 bg-white/5 p-12 text-center backdrop-blur"
      >
        <div className="mx-auto mb-6 flex h-16 w-16 items-center justify-center rounded-full border border-white/10 bg-white/10">
          <Clock className="h-7 w-7 text-slate-300" />
        </div>
        <h4 className="text-xl font-medium text-slate-100">История пуста</h4>
        <p className="mt-3 text-sm text-slate-400">
          Запустите сканирование новостей, чтобы создать первую запись в истории.
        </p>
      </motion.div>
    );
  }

  return (
    <div className="space-y-4">
      {runs.map((run, index) => (
        <motion.div
          key={run.id}
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: index * 0.05 }}
          onClick={() => onRunClick(run.id)}
          className="group cursor-pointer rounded-2xl border border-white/10 bg-gradient-to-br from-white/8 via-slate-900/25 to-slate-900/45 p-6 backdrop-blur-sm transition-all hover:border-cyan-500/40 hover:shadow-lg hover:shadow-cyan-500/10"
        >
          <div className="flex items-start justify-between gap-4">
            <div className="flex-1">
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-br from-cyan-400/20 to-blue-500/20 ring-1 ring-cyan-400/30">
                  <FileText className="h-5 w-5 text-cyan-300" />
                </div>
                <div>
                  <p className="text-sm font-medium text-slate-300">
                    {new Date(run.created_at).toLocaleString('ru-RU', {
                      year: 'numeric',
                      month: 'short',
                      day: 'numeric',
                      hour: '2-digit',
                      minute: '2-digit',
                    })}
                  </p>
                  <p className="text-xs text-slate-500">ID запуска: #{run.id}</p>
                </div>
              </div>

              <div className="mt-4 grid grid-cols-2 gap-3 sm:grid-cols-4">
                <div className="rounded-lg border border-white/5 bg-white/5 p-3">
                  <div className="flex items-center gap-2 text-xs text-slate-400">
                    <TrendingUp className="h-3.5 w-3.5" />
                    <span>Stories</span>
                  </div>
                  <p className="mt-1 text-lg font-semibold text-slate-100">
                    {run.story_count}
                  </p>
                </div>

                <div className="rounded-lg border border-white/5 bg-white/5 p-3">
                  <div className="flex items-center gap-2 text-xs text-slate-400">
                    <FileText className="h-3.5 w-3.5" />
                    <span>Статьи</span>
                  </div>
                  <p className="mt-1 text-lg font-semibold text-slate-100">
                    {run.total_articles_processed}
                  </p>
                </div>

                <div className="rounded-lg border border-white/5 bg-white/5 p-3">
                  <div className="flex items-center gap-2 text-xs text-slate-400">
                    <Clock className="h-3.5 w-3.5" />
                    <span>Окно</span>
                  </div>
                  <p className="mt-1 text-lg font-semibold text-slate-100">
                    {run.time_window_hours}ч
                  </p>
                </div>

                <div className="rounded-lg border border-white/5 bg-white/5 p-3">
                  <div className="flex items-center gap-2 text-xs text-slate-400">
                    <Zap className="h-3.5 w-3.5" />
                    <span>Время</span>
                  </div>
                  <p className="mt-1 text-lg font-semibold text-slate-100">
                    {Math.round(run.processing_time_seconds)}с
                  </p>
                </div>
              </div>
            </div>

            <div className="flex flex-col items-end gap-2">
              <div className="rounded-full bg-gradient-to-br from-cyan-400/20 to-blue-500/20 px-3 py-1 text-xs font-semibold uppercase tracking-wider text-cyan-300 ring-1 ring-cyan-400/30">
                {run.story_count} {run.story_count === 1 ? 'сюжет' : 'сюжетов'}
              </div>
              <div className="text-xs text-slate-500">
                Порог: {(run.hotness_threshold * 100).toFixed(0)}%
              </div>
            </div>
          </div>

          <div className="mt-4 flex items-center gap-2 text-xs text-cyan-400 opacity-0 transition-opacity group-hover:opacity-100">
            <span>Нажмите для просмотра деталей</span>
            <svg
              className="h-4 w-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 5l7 7-7 7"
              />
            </svg>
          </div>
        </motion.div>
      ))}
    </div>
  );
}

