'use client';

import { HotnessScore } from '@/lib/types';
import { motion } from 'framer-motion';

interface HotnessMetricsProps {
  hotness: HotnessScore;
}

const metrics = [
  { key: 'unexpectedness', label: 'Неожиданность', gradient: 'from-cyan-400 via-blue-500 to-indigo-600' },
  { key: 'materiality', label: 'Значимость', gradient: 'from-emerald-400 via-cyan-500 to-sky-600' },
  { key: 'velocity', label: 'Скорость', gradient: 'from-purple-400 via-indigo-500 to-blue-600' },
  { key: 'breadth', label: 'Охват', gradient: 'from-amber-400 via-orange-500 to-rose-500' },
  { key: 'credibility', label: 'Достоверность', gradient: 'from-slate-400 via-slate-500 to-slate-600' },
];

export default function HotnessMetrics({ hotness }: HotnessMetricsProps) {
  return (
    <div className="space-y-4">
      {metrics.map((metric, index) => {
        const value = hotness[metric.key as keyof Omit<HotnessScore, 'overall' | 'reasoning'>] as number;
        const percentage = Math.round(value * 100);

        return (
          <div key={metric.key} className="space-y-2">
            <div className="flex items-baseline justify-between text-xs uppercase tracking-[0.3em] text-slate-400">
              <span>{metric.label}</span>
              <span className="text-slate-200">{percentage} %</span>
            </div>
            <div className="h-2.5 overflow-hidden rounded-full border border-white/10 bg-white/10">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${percentage}%` }}
                transition={{ duration: 0.8, delay: index * 0.05 }}
                className={`h-full rounded-full bg-gradient-to-r ${metric.gradient}`}
              />
            </div>
          </div>
        );
      })}
    </div>
  );
}

