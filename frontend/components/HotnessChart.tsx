'use client';

import { HotnessScore } from '@/lib/types';
import { PolarAngleAxis, PolarGrid, PolarRadiusAxis, Radar, RadarChart, ResponsiveContainer } from 'recharts';

interface HotnessChartProps {
  hotness: HotnessScore;
}

export default function HotnessChart({ hotness }: HotnessChartProps) {
  const data = [
    {
      metric: 'Неожиданность',
      value: hotness.unexpectedness * 100,
      fullMark: 100,
    },
    {
      metric: 'Значимость',
      value: hotness.materiality * 100,
      fullMark: 100,
    },
    {
      metric: 'Скорость',
      value: hotness.velocity * 100,
      fullMark: 100,
    },
    {
      metric: 'Охват',
      value: hotness.breadth * 100,
      fullMark: 100,
    },
    {
      metric: 'Достоверность',
      value: hotness.credibility * 100,
      fullMark: 100,
    },
  ];

  return (
    <div className="h-64 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <RadarChart cx="50%" cy="50%" outerRadius="78%" data={data}>
          <PolarGrid stroke="rgba(148, 163, 184, 0.2)" radialLines={false} />
          <PolarAngleAxis dataKey="metric" tick={{ fill: '#cbd5f5', fontSize: 11, letterSpacing: '0.08em' }} stroke="none" />
          <PolarRadiusAxis
            stroke="rgba(148, 163, 184, 0.15)"
            domain={[0, 100]}
            tick={{ fill: 'rgba(148, 163, 184, 0.65)', fontSize: 9 }}
            tickSize={2}
          />
          <Radar
            name="Hotness"
            dataKey="value"
            stroke="url(#radarStroke)"
            fill="url(#radarFill)"
            strokeWidth={2.5}
            fillOpacity={0.55}
          />
          <defs>
            <linearGradient id="radarStroke" x1="0" y1="0" x2="1" y2="1">
              <stop offset="0%" stopColor="#22d3ee" />
              <stop offset="50%" stopColor="#6366f1" />
              <stop offset="100%" stopColor="#7c3aed" />
            </linearGradient>
            <linearGradient id="radarFill" x1="0" y1="0" x2="1" y2="1">
              <stop offset="0%" stopColor="rgba(34, 211, 238, 0.35)" />
              <stop offset="100%" stopColor="rgba(124, 58, 237, 0.25)" />
            </linearGradient>
          </defs>
        </RadarChart>
      </ResponsiveContainer>
    </div>
  );
}

