'use client';

import { useEffect, useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { Activity, AlertCircle, Clock, LineChart, ShieldCheck, Sparkle } from 'lucide-react';
import Link from 'next/link';
import ControlPanel from '@/components/ControlPanel';
import StoryCard from '@/components/StoryCard';
import StatsDisplay from '@/components/StatsDisplay';
import MoneyBackground from '@/components/MoneyBackground';
import { radarApi } from '@/lib/api';
import { ProcessRequest, RadarResponse } from '@/lib/types';

const heroHighlights = [
  {
    title: 'Многомерный скоринг',
    copy: 'Неожиданность, материальность, скорость, охват и достоверность — единая шкала приоритизации.',
  },
  {
    title: 'Интеллектуальное исследование',
    copy: 'Автоматический deep research для приоритетных сюжетов с расширенной ссылочной базой.',
  },
  {
    title: 'Премиальные черновики',
    copy: 'Структурированные тексты с атрибуцией и рыночным контекстом, готовые к коммуникациям.',
  },
];

export default function Home() {
  const [data, setData] = useState<RadarResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isHealthy, setIsHealthy] = useState(false);

  useEffect(() => {
    const init = async () => {
      await checkHealth();
      
      // Check if we have a result from history page
      const storedResult = sessionStorage.getItem('radarResult');
      if (storedResult) {
        try {
          const result = JSON.parse(storedResult);
          setData(result);
          sessionStorage.removeItem('radarResult');
        } catch (err) {
          console.error('Error parsing stored result:', err);
        }
      } else {
        await loadLastResult();
      }
    };

    init();
  }, []);

  const checkHealth = async () => {
    try {
      const health = await radarApi.healthCheck();
      setIsHealthy(health.status === 'healthy');
    } catch (err) {
      setIsHealthy(false);
      console.error('Health check failed:', err);
    }
  };

  const loadLastResult = async () => {
    try {
      const result = await radarApi.getLastResult();
      setData(result);
    } catch {
      // cached result отсутствует — допустимо
    }
  };

  const handleScan = async (request: ProcessRequest) => {
    setIsLoading(true);
    setError(null);

    try {
      const result = await radarApi.processNews(request);
      setData(result);
    } catch (err: unknown) {
      const errorMessage = err && typeof err === 'object' && 'response' in err
        ? (err.response as { data?: { detail?: string } })?.data?.detail || 'Не удалось обработать новости'
        : err instanceof Error
        ? err.message
        : 'Не удалось обработать новости';
      setError(errorMessage);
      console.error('Error processing news:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const avgHotness = data
    ? data.stories.reduce((sum, story) => sum + story.hotness, 0) / data.stories.length
    : 0;

  return (
    <div className="relative min-h-screen overflow-hidden bg-[#05070f] text-slate-100">
      <MoneyBackground />
      <div className="pointer-events-none absolute inset-0 z-0">
        <div className="absolute inset-x-0 top-0 h-[520px] bg-[radial-gradient(circle_at_top,rgba(14,116,144,0.35)_0%,rgba(5,7,15,0.4)_55%,rgba(5,7,15,0)_100%)]" />
        <div className="absolute -left-20 top-44 h-72 w-72 rounded-full bg-gradient-to-br from-cyan-500/20 via-blue-500/10 to-transparent blur-3xl" />
        <div className="absolute right-0 top-64 h-96 w-96 rounded-full bg-gradient-to-br from-indigo-600/10 via-purple-500/10 to-transparent blur-3xl" />
      </div>

      <header className="sticky top-0 z-40 border-b border-white/10 bg-[#05070f]/80 backdrop-blur-xl">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-4 lg:px-8">
          <div className="flex items-center gap-3">
            <div className="flex h-12 w-12 items-center justify-center rounded-full bg-gradient-to-br from-cyan-400 via-blue-500 to-indigo-600 shadow-lg shadow-cyan-500/25">
              <LineChart className="h-6 w-6 text-white" />
            </div>
            <div>
              <h1 className="text-sm font-semibold uppercase tracking-[0.32em] text-slate-200">Radar Intelligence</h1>
              <p className="text-xs text-slate-400">Финансовый мониторинг горячих событий</p>
            </div>
          </div>
          
          <div className="flex items-center gap-3">
            <Link
              href="/history"
              className="flex items-center gap-2 rounded-lg border border-white/10 bg-white/5 px-4 py-2 text-xs font-medium text-slate-300 transition-all hover:border-cyan-500/40 hover:bg-white/10"
            >
              <Clock className="h-3.5 w-3.5" />
              История
            </Link>
            
            <div
              className={`flex items-center gap-2 rounded-full border px-4 py-1.5 text-xs font-semibold uppercase tracking-[0.3em] text-slate-300 ${
                isHealthy ? 'border-emerald-500/40 text-emerald-300' : 'border-rose-500/40 text-rose-300'
              }`}
            >
              <Activity className="h-3.5 w-3.5" />
              {isHealthy ? 'Backend Online' : 'Backend Offline'}
            </div>
          </div>
        </div>
      </header>

      <main className="relative mx-auto max-w-6xl px-4 pb-20 lg:px-8">
        <section className="grid gap-12 py-16 lg:grid-cols-[1.2fr,0.8fr] lg:items-center">
          <motion.div
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="space-y-8"
          >
            <div className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-4 py-2 text-[0.7rem] uppercase tracking-[0.35em] text-slate-300">
              <ShieldCheck className="h-4 w-4 text-cyan-300" />
              Контроль достоверности • Таймлайн подтверждений
            </div>
            <div className="space-y-4">
              <h2 className="text-4xl font-semibold leading-tight text-slate-50 md:text-5xl">
                Финансовый радар для мгновенной оценки рыночных событий
              </h2>
              <p className="max-w-xl text-lg text-slate-400">
                Получайте отфильтрованные горячие сюжеты, прозрачную аналитику по пяти критериям «горячести» и готовые к публикации материалы в тональности инвестиционных банков.
              </p>
            </div>
            <div className="grid gap-4 md:grid-cols-3">
              {heroHighlights.map((item) => (
                <div
                  key={item.title}
                  className="rounded-2xl border border-white/10 bg-gradient-to-br from-white/8 via-slate-900/25 to-slate-900/45 p-5 backdrop-blur-sm"
                >
                  <h3 className="mb-2 text-xs font-semibold uppercase tracking-[0.3em] text-slate-200">{item.title}</h3>
                  <p className="text-sm text-slate-400">{item.copy}</p>
                </div>
              ))}
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 32 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.15 }}
            className="relative"
          >
            <div className="absolute inset-0 -z-10 rounded-3xl bg-gradient-to-br from-cyan-500/25 via-blue-500/10 to-transparent blur-2xl" />
            <ControlPanel onScan={handleScan} isLoading={isLoading} />
          </motion.div>
        </section>

        <AnimatePresence>
          {error && (
            <motion.div
              initial={{ opacity: 0, y: -12 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -12 }}
              className="mb-12 rounded-2xl border border-rose-500/40 bg-rose-950/60 p-6 text-sm text-rose-200 backdrop-blur"
            >
              <div className="flex items-start gap-3">
                <AlertCircle className="mt-0.5 h-5 w-5 text-rose-300" />
                <div>
                  <p className="font-semibold uppercase tracking-[0.28em] text-rose-200/80">Ошибка обработки</p>
                  <p className="mt-1 text-rose-100/80">{error}</p>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {data ? (
          <section className="space-y-12">
            <StatsDisplay
              storyCount={data.stories.length}
              articleCount={data.total_articles_processed}
              processingTime={data.processing_time_seconds}
              avgHotness={avgHotness}
            />

            {data.stories.length > 0 ? (
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.5 }}>
                <div className="mb-10 flex flex-wrap items-center justify-between gap-4">
                  <div>
                    <h3 className="text-2xl font-semibold text-slate-100">Лента горячих сюжетов</h3>
                    <p className="text-sm text-slate-500">
                      Сформировано {new Date(data.generated_at).toLocaleString('ru-RU')} • приоритет по интегральному scoringu
                    </p>
                  </div>
                  <div className="flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs uppercase tracking-[0.35em] text-slate-300">
                    <Sparkle className="h-3.5 w-3.5 text-cyan-300" />
                    {data.total_articles_processed} источников обработано
                  </div>
                </div>

                <div className="space-y-10">
                  {data.stories.map((story, index) => (
                    <StoryCard key={story.id} story={story} index={index} />
                  ))}
                </div>
              </motion.div>
            ) : (
              <motion.div
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                className="rounded-3xl border border-white/10 bg-white/5 p-12 text-center backdrop-blur"
              >
                <div className="mx-auto mb-6 flex h-16 w-16 items-center justify-center rounded-full border border-white/10 bg-white/10">
                  <LineChart className="h-7 w-7 text-slate-300" />
                </div>
                <h4 className="text-xl font-medium text-slate-100">Горячие сюжеты не обнаружены</h4>
                <p className="mt-3 text-sm text-slate-400">
                  Расширьте временное окно или снизьте порог горячести, чтобы увидеть более широкий спектр новостей.
                </p>
              </motion.div>
            )}
          </section>
        ) : (
          !isLoading && (
            <motion.section
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              className="mt-6 rounded-3xl border border-white/10 bg-white/5 p-12 text-center backdrop-blur"
            >
              <div className="mx-auto mb-6 flex h-16 w-16 items-center justify-center rounded-full border border-white/10 bg-white/10">
                <ShieldCheck className="h-7 w-7 text-cyan-300" />
              </div>
              <h3 className="text-2xl font-semibold text-slate-100">Эталонный мониторинг готов к запуску</h3>
              <p className="mx-auto mt-3 max-w-2xl text-sm text-slate-400">
                Настройте параметры сканирования справа, чтобы получить отранжированные события, детализированный таймлайн и готовые к коммуникациям материалы.
              </p>
            </motion.section>
          )
        )}
      </main>

      <footer className="border-t border-white/10 bg-[#05070f]/80 py-10 backdrop-blur">
        <div className="mx-auto flex max-w-6xl flex-col items-center gap-2 px-4 text-[0.65rem] uppercase tracking-[0.32em] text-slate-500 lg:px-8">
          <span>Radar Intelligence Platform</span>
          <span className="text-slate-600">Gemini • GPT Researcher • Tavily Orchestration</span>
        </div>
      </footer>
    </div>
  );
}
