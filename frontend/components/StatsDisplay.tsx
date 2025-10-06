'use client';

import { motion } from 'framer-motion';
import { Clock, Layers, LineChart, Zap } from 'lucide-react';

interface StatsDisplayProps {
  storyCount: number;
  articleCount: number;
  processingTime: number;
  avgHotness: number;
}

const statCards = [
  {
    key: 'stories',
    icon: LineChart,
    label: 'Горячих сюжетов',
    color: 'from-cyan-400 via-blue-500 to-indigo-600',
  },
  {
    key: 'articles',
    icon: Layers,
    label: 'Статей обработано',
    color: 'from-emerald-400 via-cyan-500 to-sky-600',
  },
  {
    key: 'processing',
    icon: Clock,
    label: 'Время обработки',
    color: 'from-slate-400 via-slate-500 to-slate-600',
  },
  {
    key: 'hotness',
    icon: Zap,
    label: 'Средняя горячесть',
    color: 'from-amber-400 via-orange-500 to-rose-500',
  },
];

export default function StatsDisplay({
  storyCount,
  articleCount,
  processingTime,
  avgHotness,
}: StatsDisplayProps) {
  const values: Record<string, string | number> = {
    stories: storyCount,
    articles: articleCount,
    processing: `${processingTime.toFixed(1)} c`,
    hotness: `${(avgHotness * 100).toFixed(0)} %`,
  };

  return (
    <div className="grid grid-cols-1 gap-6 md:grid-cols-2 xl:grid-cols-4">
      {statCards.map((stat, index) => (
        <motion.div
          key={stat.key}
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: index * 0.08 }}
          className="relative overflow-hidden rounded-3xl border border-white/10 bg-white/5 p-6 text-slate-100 backdrop-blur"
        >
          <div className="absolute inset-0 opacity-70">
            <div className={`absolute inset-0 bg-gradient-to-br ${stat.color} mix-blend-soft-light`} />
            <div className="absolute -right-8 -top-8 h-32 w-32 rounded-full bg-white/10 blur-3xl" />
          </div>

          <div className="relative z-10 flex items-start justify-between">
            <div>
              <p className="text-[0.65rem] uppercase tracking-[0.32em] text-slate-300">{stat.label}</p>
              <p className="mt-3 text-3xl font-semibold tracking-tight text-slate-50">
                {values[stat.key]}
              </p>
            </div>
            <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-white/10 text-white">
              <stat.icon className="h-5 w-5" />
            </div>
          </div>
        </motion.div>
      ))}
    </div>
  );
}

