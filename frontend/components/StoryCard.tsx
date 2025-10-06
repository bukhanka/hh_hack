'use client';

import { useMemo, useState } from 'react';
import { NewsStory } from '@/lib/types';
import { AnimatePresence, motion } from 'framer-motion';
import {
  BarChart3,
  Building2,
  ChevronDown,
  ChevronUp,
  Clock,
  ExternalLink,
  Flame,
  Globe,
  Layers,
  TrendingUp,
  User,
} from 'lucide-react';
import { format } from 'date-fns';
import HotnessMetrics from './HotnessMetrics';
import HotnessChart from './HotnessChart';

interface StoryCardProps {
  story: NewsStory;
  index: number;
}

const entityIcons = {
  company: Building2,
  sector: BarChart3,
  country: Globe,
  person: User,
  ticker: TrendingUp,
};

const badgeStyles = [
  'from-cyan-400 via-blue-500 to-indigo-600',
  'from-emerald-400 via-cyan-500 to-sky-600',
  'from-purple-400 via-indigo-500 to-blue-600',
  'from-amber-400 via-orange-500 to-rose-500',
];

export default function StoryCard({ story, index }: StoryCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [showDraft, setShowDraft] = useState(false);

  const badgeGradient = useMemo(
    () => badgeStyles[index % badgeStyles.length],
    [index]
  );

  const hotnessValue = Math.round(story.hotness * 100);

  return (
    <motion.article
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: index * 0.08 }}
      className="overflow-hidden rounded-3xl border border-white/10 bg-white/5 text-slate-100 shadow-[0_35px_120px_-60px_rgba(14,116,144,0.65)] backdrop-blur"
    >
      <div className="border-b border-white/10 px-6 py-6">
        <div className="flex flex-col gap-6 lg:flex-row lg:items-start lg:justify-between">
          <div className="space-y-5">
            <div className="flex flex-wrap items-center gap-3 text-xs uppercase tracking-[0.32em] text-slate-400">
              <span className="rounded-full border border-white/10 px-3 py-1">#{String(index + 1).padStart(2, '0')}</span>
              {story.has_deep_research && (
                <span className="flex items-center gap-2 rounded-full border border-cyan-400/40 bg-cyan-950/40 px-3 py-1 text-cyan-200">
                  <Layers className="h-3.5 w-3.5" />
                  Deep Research
                </span>
              )}
              <span className="rounded-full border border-white/10 px-3 py-1 text-slate-500">{story.article_count} источников</span>
            </div>

            <h2 className="text-2xl font-semibold tracking-tight text-slate-50 lg:text-[28px]">
              {story.headline}
            </h2>

            <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
              <div className="flex items-start gap-3">
                <Flame className="mt-1 h-5 w-5 text-cyan-300" />
                <div>
                  <p className="text-xs uppercase tracking-[0.32em] text-slate-400">Почему важно сейчас</p>
                  <p className="mt-2 text-sm text-slate-200/85">{story.why_now}</p>
                </div>
              </div>
            </div>

            <div className="flex flex-wrap gap-2">
              {story.entities.slice(0, 8).map((entity, idx) => {
                const Icon = entityIcons[entity.type as keyof typeof entityIcons] || Building2;
                return (
                  <span
                    key={`${entity.name}-${idx}`}
                    className="flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs uppercase tracking-[0.22em] text-slate-200"
                  >
                    <Icon className="h-3.5 w-3.5 text-cyan-200" />
                    {entity.name}
                    {entity.ticker && (
                      <span className="text-cyan-300">[{entity.ticker}]</span>
                    )}
                  </span>
                );
              })}
            </div>
          </div>

          <div className="flex flex-col items-center gap-3">
            <div className={`relative flex h-28 w-28 flex-col items-center justify-center rounded-[28px] border border-white/10 bg-gradient-to-br ${badgeGradient} text-white shadow-lg shadow-cyan-500/30`}>
              <span className="text-4xl font-semibold tracking-tight">{hotnessValue}</span>
              <span className="text-[0.55rem] uppercase tracking-[0.4em] text-white/80">Hotness</span>
            </div>
            <div className="text-[0.7rem] uppercase tracking-[0.32em] text-slate-500">Integr.score</div>
          </div>
        </div>
      </div>

      <div className="border-b border-white/5 px-6 py-4">
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="flex w-full items-center justify-between text-xs uppercase tracking-[0.32em] text-slate-300 transition-colors hover:text-slate-100"
        >
          <span>Детализированный анализ</span>
          {isExpanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
        </button>
      </div>

      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.28 }}
            className="overflow-hidden"
          >
            <div className="space-y-8 border-t border-white/10 bg-[#070b13]/80 px-6 py-6 backdrop-blur">
              <div className="grid gap-6 lg:grid-cols-2">
                <div className="space-y-4">
                  <div className="flex items-center gap-2 text-xs uppercase tracking-[0.32em] text-slate-400">
                    <BarChart3 className="h-4 w-4 text-cyan-300" />
                    <span>Метрики горячести</span>
                  </div>
                  <HotnessMetrics hotness={story.hotness_details} />
                </div>
                <div className="space-y-4">
                  <p className="text-xs uppercase tracking-[0.32em] text-center text-slate-400">Профиль индикаторов</p>
                  <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
                    <HotnessChart hotness={story.hotness_details} />
                  </div>
                </div>
              </div>

              <div className="rounded-2xl border border-white/10 bg-white/5 p-5">
                <p className="text-xs uppercase tracking-[0.32em] text-slate-400">Обоснование scorинга</p>
                <p className="mt-3 text-sm leading-relaxed text-slate-200/85">
                  {story.hotness_details.reasoning}
                </p>
              </div>

              {story.timeline.length > 0 && (
                <div className="space-y-4">
                  <div className="flex items-center gap-2 text-xs uppercase tracking-[0.32em] text-slate-400">
                    <Clock className="h-4 w-4 text-cyan-300" />
                    <span>Таймлайн подтверждений</span>
                  </div>
                  <div className="space-y-3">
                    {story.timeline.map((event, idx) => (
                      <div key={`${event.timestamp}-${idx}`} className="flex gap-4">
                        <div className="w-28 flex-shrink-0 text-[0.7rem] uppercase tracking-[0.28em] text-slate-500">
                          {format(new Date(event.timestamp), 'dd MMM • HH:mm')}
                        </div>
                        <div className="flex-1 rounded-2xl border border-white/10 bg-white/5 p-4">
                          <div className="flex items-center gap-2 text-[0.6rem] uppercase tracking-[0.35em] text-cyan-200">
                            {event.event_type}
                          </div>
                          <p className="mt-2 text-sm text-slate-200/90">{event.description}</p>
                          <a
                            href={event.source_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="mt-3 inline-flex items-center gap-2 text-[0.65rem] uppercase tracking-[0.32em] text-cyan-300 transition-colors hover:text-cyan-200"
                          >
                            Смотреть источник
                            <ExternalLink className="h-3 w-3" />
                          </a>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div className="space-y-4">
                <button
                  onClick={() => setShowDraft(!showDraft)}
                  className="flex w-full items-center justify-between rounded-2xl border border-white/10 bg-gradient-to-r from-cyan-400 via-blue-500 to-indigo-600 px-5 py-3 text-xs font-semibold uppercase tracking-[0.35em] text-white transition-all hover:shadow-lg hover:shadow-cyan-500/20"
                >
                  <span>{showDraft ? 'Скрыть черновик' : 'Показать черновик'}</span>
                  {showDraft ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
                </button>

                <AnimatePresence>
                  {showDraft && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: 'auto', opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      className="overflow-hidden"
                    >
                      <div className="rounded-2xl border border-white/10 bg-white/5 p-6 text-slate-100">
                        <div
                          className="prose prose-invert prose-sm max-w-none"
                          dangerouslySetInnerHTML={{
                            __html: story.draft
                              .replace(/^### (.*$)/gim, '<h3 class="text-lg font-semibold tracking-tight mt-6 mb-3">$1</h3>')
                              .replace(/^## (.*$)/gim, '<h2 class="text-xl font-semibold tracking-tight mt-6 mb-3">$1</h2>')
                              .replace(/^# (.*$)/gim, '<h1 class="text-2xl font-semibold tracking-tight mt-6 mb-3">$1</h1>')
                              .replace(/^\* (.*$)/gim, '<li class="mb-1">$1</li>')
                              .replace(/^\• (.*$)/gim, '<li class="mb-1">$1</li>')
                              .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                              .replace(/\n\n/g, '</p><p class="mb-4">'),
                          }}
                        />
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>

              <div>
                <p className="text-xs uppercase tracking-[0.32em] text-slate-400">Ключевые источники ({story.sources.length})</p>
                <div className="mt-3 grid gap-2">
                  {story.sources.slice(0, 6).map((url, idx) => (
                    <a
                      key={`${url}-${idx}`}
                      href={url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-2 rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-[0.7rem] uppercase tracking-[0.28em] text-cyan-300 transition-colors hover:text-cyan-200"
                    >
                      <ExternalLink className="h-4 w-4" />
                      <span className="truncate">{url}</span>
                    </a>
                  ))}
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.article>
  );
}

