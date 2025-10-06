'use client';

import { motion } from 'framer-motion';
import { TrendingUp, Newspaper, ArrowRight, Activity, Sparkles, Target, Zap } from 'lucide-react';
import Link from 'next/link';
import { useEffect, useState } from 'react';
import { radarApi } from '@/lib/api';
import { logger } from '@/lib/logger';
import MoneyBackground from '@/components/MoneyBackground';

export default function HomePage() {
  const [isHealthy, setIsHealthy] = useState(false);

  useEffect(() => {
    logger.info('Homepage initialized');
    const checkHealth = async () => {
      try {
        const health = await radarApi.healthCheck();
        setIsHealthy(health.status === 'healthy');
        logger.debug('Health check completed', { status: health.status });
      } catch (err) {
        setIsHealthy(false);
        logger.error('Health check failed', err);
      }
    };

    checkHealth();
  }, []);

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
              <Activity className="h-6 w-6 text-white" />
            </div>
            <div>
              <h1 className="text-sm font-semibold uppercase tracking-[0.32em] text-slate-200">News Intelligence</h1>
              <p className="text-xs text-slate-400">Двухрежимная платформа агрегации новостей</p>
            </div>
          </div>
          
          <div
            className={`flex items-center gap-2 rounded-full border px-4 py-1.5 text-xs font-semibold uppercase tracking-[0.3em] text-slate-300 ${
              isHealthy ? 'border-emerald-500/40 text-emerald-300' : 'border-rose-500/40 text-rose-300'
            }`}
          >
            <Activity className="h-3.5 w-3.5" />
            {isHealthy ? 'Backend Online' : 'Backend Offline'}
          </div>
        </div>
      </header>

      <main className="relative mx-auto max-w-6xl px-4 pb-20 pt-20 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="mb-16 text-center"
        >
          <div className="mx-auto mb-6 inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-4 py-2 text-xs font-medium tracking-wider text-slate-300">
            <Zap className="h-3.5 w-3.5 text-cyan-300" />
            Powered by Gemini AI · GPT Researcher · Tavily
          </div>
          
          <h1 className="mb-6 text-5xl font-semibold leading-tight text-slate-50 md:text-6xl">
            Выберите режим работы
          </h1>
          
          <p className="mx-auto max-w-2xl text-lg text-slate-400">
            Универсальная платформа для анализа новостей: от финансовых рынков до персонализированной ленты
          </p>
        </motion.div>

        <div className="grid gap-8 md:grid-cols-2">
          {/* Financial RADAR Mode */}
          <motion.div
            initial={{ opacity: 0, y: 32 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.1 }}
          >
            <Link href="/financial">
              <div className="group relative overflow-hidden rounded-3xl border border-white/10 bg-gradient-to-br from-white/8 via-slate-900/25 to-slate-900/45 p-8 backdrop-blur transition-all hover:border-cyan-500/40 hover:shadow-2xl hover:shadow-cyan-500/10">
                <div className="absolute -right-10 -top-10 h-40 w-40 rounded-full bg-gradient-to-br from-cyan-500/20 to-blue-500/10 blur-3xl transition-all group-hover:scale-150" />
                
                <div className="relative">
                  <div className="mb-6 flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-cyan-400 via-blue-500 to-indigo-600 shadow-lg shadow-cyan-500/25">
                    <TrendingUp className="h-8 w-8 text-white" />
                  </div>
                  
                  <h2 className="mb-3 text-3xl font-semibold text-slate-50">Financial RADAR</h2>
                  
                  <p className="mb-6 text-sm text-slate-400">
                    Система выявления и оценки горячих новостей на финансовых рынках с детальной аналитикой по 5 критериям
                  </p>
                  
                  <div className="mb-6 space-y-3">
                    <div className="flex items-start gap-3">
                      <div className="mt-0.5 flex h-6 w-6 items-center justify-center rounded-lg bg-cyan-500/10">
                        <Target className="h-3.5 w-3.5 text-cyan-400" />
                      </div>
                      <span className="text-sm leading-relaxed text-slate-300">Многомерный скоринг горячести</span>
                    </div>
                    <div className="flex items-start gap-3">
                      <div className="mt-0.5 flex h-6 w-6 items-center justify-center rounded-lg bg-cyan-500/10">
                        <Sparkles className="h-3.5 w-3.5 text-cyan-400" />
                      </div>
                      <span className="text-sm leading-relaxed text-slate-300">Автоматический deep research</span>
                    </div>
                    <div className="flex items-start gap-3">
                      <div className="mt-0.5 flex h-6 w-6 items-center justify-center rounded-lg bg-cyan-500/10">
                        <TrendingUp className="h-3.5 w-3.5 text-cyan-400" />
                      </div>
                      <span className="text-sm leading-relaxed text-slate-300">Готовые черновики публикаций</span>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-2 text-cyan-400 transition-all group-hover:gap-4">
                    <span className="text-sm font-semibold uppercase tracking-wider">Запустить RADAR</span>
                    <ArrowRight className="h-5 w-5" />
                  </div>
                </div>
              </div>
            </Link>
          </motion.div>

          {/* Personal News Aggregator Mode */}
          <motion.div
            initial={{ opacity: 0, y: 32 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
          >
            <div className="group relative overflow-hidden rounded-3xl border border-white/10 bg-gradient-to-br from-white/8 via-slate-900/25 to-slate-900/45 p-8 backdrop-blur transition-all hover:border-purple-500/40 hover:shadow-2xl hover:shadow-purple-500/10">
              <div className="absolute -right-10 -top-10 h-40 w-40 rounded-full bg-gradient-to-br from-purple-500/20 to-pink-500/10 blur-3xl transition-all group-hover:scale-150" />
              
              <div className="relative">
                <div className="mb-6 flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-purple-400 via-pink-500 to-rose-600 shadow-lg shadow-purple-500/25">
                  <Newspaper className="h-8 w-8 text-white" />
                </div>
                
                <h2 className="mb-3 text-3xl font-semibold text-slate-50">Personal Aggregator</h2>
                
                <p className="mb-6 text-sm text-slate-400">
                  Персонализированный агрегатор новостей с умным обучением на основе ваших предпочтений
                </p>
                
                <div className="mb-6 space-y-3">
                  <div className="flex items-start gap-3">
                    <div className="mt-0.5 flex h-6 w-6 items-center justify-center rounded-lg bg-purple-500/10">
                      <Sparkles className="h-3.5 w-3.5 text-purple-400" />
                    </div>
                    <span className="text-sm leading-relaxed text-slate-300">Умное обучение на взаимодействиях</span>
                  </div>
                  <div className="flex items-start gap-3">
                    <div className="mt-0.5 flex h-6 w-6 items-center justify-center rounded-lg bg-purple-500/10">
                      <Target className="h-3.5 w-3.5 text-purple-400" />
                    </div>
                    <span className="text-sm leading-relaxed text-slate-300">Лайки, сохранения, персистентная лента</span>
                  </div>
                  <div className="flex items-start gap-3">
                    <div className="mt-0.5 flex h-6 w-6 items-center justify-center rounded-lg bg-purple-500/10">
                      <Activity className="h-3.5 w-3.5 text-purple-400" />
                    </div>
                    <span className="text-sm leading-relaxed text-slate-300">Статистика и аналитика активности</span>
                  </div>
                </div>
                
                <div className="flex flex-col gap-3">
                  <Link href="/onboarding" className="block">
                    <div className="flex items-center justify-between rounded-xl border border-purple-500/40 bg-gradient-to-r from-purple-500 to-pink-500 px-4 py-3 transition-all hover:border-purple-400 hover:shadow-lg hover:shadow-purple-500/25">
                      <span className="text-sm font-semibold uppercase tracking-wider text-white">Начать Онбординг</span>
                      <ArrowRight className="h-5 w-5 text-white" />
                    </div>
                  </Link>
                  <Link href="/personal" className="block">
                    <div className="flex items-center justify-between rounded-xl border border-white/10 bg-white/5 px-4 py-3 transition-all hover:border-purple-500/40">
                      <span className="text-sm font-semibold uppercase tracking-wider text-purple-400">Открыть Ленту</span>
                      <ArrowRight className="h-5 w-5 text-purple-400" />
                    </div>
                  </Link>
                </div>
              </div>
            </div>
          </motion.div>
        </div>

        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
          className="mt-16 overflow-hidden rounded-3xl border border-white/10 bg-gradient-to-br from-white/5 to-white/[0.02] backdrop-blur"
        >
          <div className="border-b border-white/10 px-8 py-5">
            <h3 className="text-xl font-semibold text-slate-100">Единая инфраструктура</h3>
          </div>
          <div className="px-8 py-6">
            <p className="mx-auto max-w-3xl leading-relaxed text-slate-400">
              Оба режима используют общие компоненты: сбор новостей из RSS и Tavily, дедупликацию статей, базу данных и историю обработки. 
              Выберите финансовый режим для глубокого анализа рынков или персональный режим для быстрого обзора новостей из выбранных источников.
            </p>
          </div>
        </motion.div>
      </main>

      <footer className="border-t border-white/10 bg-[#05070f]/80 py-10 backdrop-blur">
        <div className="mx-auto flex max-w-6xl flex-col items-center gap-2 px-4 text-[0.65rem] uppercase tracking-[0.32em] text-slate-500 lg:px-8">
          <span>News Intelligence Platform v2.0</span>
          <span className="text-slate-600">Two Modes • One Infrastructure</span>
        </div>
      </footer>
    </div>
  );
}
