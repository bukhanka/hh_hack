'use client';

import { useState } from 'react';
import { ProcessRequest } from '@/lib/types';
import { Gauge, Zap } from 'lucide-react';
import { motion } from 'framer-motion';

interface ControlPanelProps {
  onScan: (request: ProcessRequest) => void;
  isLoading: boolean;
}

export default function ControlPanel({ onScan, isLoading }: ControlPanelProps) {
  const [timeWindow, setTimeWindow] = useState(24);
  const [topK, setTopK] = useState(10);
  const [threshold, setThreshold] = useState(0.5);

  const handleScan = () => {
    onScan({
      time_window_hours: timeWindow,
      top_k: topK,
      hotness_threshold: threshold,
    });
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 24 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="rounded-3xl border border-white/10 bg-[#0b111d]/80 p-8 text-slate-100 shadow-[0_25px_80px_-40px_rgba(14,116,144,0.6)] backdrop-blur"
    >
      <div className="mb-6 flex items-center gap-3">
        <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-gradient-to-br from-cyan-400 via-blue-500 to-indigo-600 shadow-lg shadow-cyan-500/30">
          <Gauge className="h-5 w-5 text-white" />
        </div>
        <div>
          <h2 className="text-lg font-semibold uppercase tracking-[0.35em] text-slate-200">Сценарий сканирования</h2>
          <p className="text-xs text-slate-500">Точное управление окном, глубиной и фильтрацией горячести</p>
        </div>
      </div>

      <div className="grid gap-5 md:grid-cols-3">
        <label className="space-y-2 text-xs uppercase tracking-[0.28em] text-slate-400">
          <span>Временное окно</span>
          <div className="rounded-2xl border border-white/10 bg-white/10 px-4 py-3 text-slate-100 transition-all focus-within:border-cyan-400/60">
            <div className="flex items-center justify-between text-sm font-medium">
              <input
                type="number"
                value={timeWindow}
                onChange={(e) => setTimeWindow(Number(e.target.value))}
                min={1}
                max={168}
                className="w-full bg-transparent text-base font-semibold tracking-tight text-slate-100 outline-none"
              />
              <span className="text-xs text-slate-400">часов</span>
            </div>
          </div>
          <span className="block text-[0.65rem] normal-case tracking-normal text-slate-500">Диапазон 1–168, default 24</span>
        </label>

        <label className="space-y-2 text-xs uppercase tracking-[0.28em] text-slate-400">
          <span>Топ сюжетов</span>
          <div className="rounded-2xl border border-white/10 bg-white/10 px-4 py-3 text-slate-100 transition-all focus-within:border-cyan-400/60">
            <div className="flex items-center justify-between text-sm font-medium">
              <input
                type="number"
                value={topK}
                onChange={(e) => setTopK(Number(e.target.value))}
                min={1}
                max={50}
                className="w-full bg-transparent text-base font-semibold tracking-tight text-slate-100 outline-none"
              />
              <span className="text-xs text-slate-400">сюжетов</span>
            </div>
          </div>
          <span className="block text-[0.65rem] normal-case tracking-normal text-slate-500">Количество кластеров на вывод</span>
        </label>

        <label className="space-y-2 text-xs uppercase tracking-[0.28em] text-slate-400">
          <span>Порог горячести</span>
          <div className="rounded-2xl border border-white/10 bg-white/10 px-4 py-3 text-slate-100 transition-all focus-within:border-cyan-400/60">
            <div className="flex items-center justify-between text-sm font-medium">
              <input
                type="number"
                value={threshold}
                onChange={(e) => setThreshold(Number(e.target.value))}
                min={0}
                max={1}
                step={0.1}
                className="w-full bg-transparent text-base font-semibold tracking-tight text-slate-100 outline-none"
              />
              <span className="text-xs text-slate-400">/ 1.0</span>
            </div>
          </div>
          <span className="block text-[0.65rem] normal-case tracking-normal text-slate-500">Минимальный интегральный score</span>
        </label>
      </div>

      <button
        onClick={handleScan}
        disabled={isLoading}
        className="mt-8 flex w-full items-center justify-center gap-3 rounded-2xl bg-gradient-to-r from-cyan-400 via-blue-500 to-indigo-600 py-4 text-sm font-semibold uppercase tracking-[0.35em] text-white shadow-lg shadow-cyan-500/30 transition-all hover:shadow-cyan-500/40 disabled:cursor-not-allowed disabled:opacity-60"
      >
        {isLoading ? (
          <>
            <div className="h-5 w-5 animate-spin rounded-full border-2 border-white/40 border-t-white" />
            Обработка...
          </>
        ) : (
          <>
            <Zap className="h-5 w-5" />
            Старт сканирования
          </>
        )}
      </button>
    </motion.div>
  );
}

