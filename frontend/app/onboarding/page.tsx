'use client';

import { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ArrowRight, ArrowLeft, Check, Plus, X, Sparkles, Newspaper } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { personalApi } from '@/lib/api';
import { logger } from '@/lib/logger';
import type { OnboardingPreset } from '@/lib/types';

const ONBOARDING_STEPS = ['welcome', 'presets', 'customize', 'complete'] as const;
type OnboardingStep = typeof ONBOARDING_STEPS[number];

export default function OnboardingPage() {
  const router = useRouter();
  const [currentStep, setCurrentStep] = useState<OnboardingStep>('welcome');
  const [presets, setPresets] = useState<OnboardingPreset[]>([]);
  const [selectedPreset, setSelectedPreset] = useState<OnboardingPreset | null>(null);
  
  // User selections
  const [selectedCategories, setSelectedCategories] = useState<string[]>([]);
  const [selectedKeywords, setSelectedKeywords] = useState<string[]>([]);
  const [selectedSources, setSelectedSources] = useState<string[]>([]);
  const [newKeyword, setNewKeyword] = useState('');
  
  const [isLoading, setIsLoading] = useState(false);
  const [userId] = useState('default'); // В реальном приложении из auth

  useEffect(() => {
    logger.info('Onboarding page initialized');
    loadPresets();
  }, []);

  const loadPresets = async () => {
    try {
      const data = await personalApi.getOnboardingPresets();
      setPresets(data);
      logger.debug('Onboarding presets loaded', { count: data.length });
    } catch (err) {
      logger.error('Error loading presets', err);
    }
  };

  const handlePresetSelect = (preset: OnboardingPreset) => {
    setSelectedPreset(preset);
    setSelectedCategories(preset.categories);
    setSelectedKeywords(preset.keywords);
    setSelectedSources(preset.sources);
    logger.userAction('Preset selected', { presetName: preset.name });
  };

  const handleAddKeyword = () => {
    if (!newKeyword.trim()) return;
    setSelectedKeywords([...selectedKeywords, newKeyword.trim()]);
    setNewKeyword('');
  };

  const handleRemoveKeyword = (keyword: string) => {
    setSelectedKeywords(selectedKeywords.filter(k => k !== keyword));
  };

  const handleComplete = async () => {
    setIsLoading(true);
    logger.userAction('Onboarding completion initiated');
    const startTime = performance.now();
    
    try {
      await personalApi.completeOnboarding({
        user_id: userId,
        preset_key: selectedPreset?.preset_key,
        categories: selectedCategories,
        keywords: selectedKeywords,
        sources: selectedSources,
      });
      
      const duration = performance.now() - startTime;
      logger.performance('Onboarding completed', duration);
      logger.info('Onboarding successful', {
        preset: selectedPreset?.name,
        keywordCount: selectedKeywords.length,
        sourceCount: selectedSources.length
      });
      
      // Redirect to personal feed
      router.push('/personal');
    } catch (err) {
      logger.error('Error completing onboarding', err);
    } finally {
      setIsLoading(false);
    }
  };

  const canProceedToCustomize = selectedPreset !== null;
  const canComplete = selectedCategories.length > 0 && selectedKeywords.length > 0 && selectedSources.length > 0;

  return (
    <div className="relative min-h-screen bg-gradient-to-br from-purple-900 via-slate-900 to-indigo-900">
      {/* Background decorations */}
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute -left-20 top-20 h-96 w-96 rounded-full bg-gradient-to-br from-purple-500/20 via-pink-500/10 to-transparent blur-3xl" />
        <div className="absolute -right-20 bottom-20 h-96 w-96 rounded-full bg-gradient-to-br from-indigo-500/20 via-purple-500/10 to-transparent blur-3xl" />
      </div>
      
      <div className="relative flex min-h-screen items-center justify-center p-4">
        <div className="w-full max-w-4xl">
        {/* Progress Bar */}
        <div className="mb-8">
          <div className="flex justify-between mb-2">
            {ONBOARDING_STEPS.map((step, index) => (
              <div
                key={step}
                className={`flex-1 h-2 rounded-full mx-1 transition-all ${
                  ONBOARDING_STEPS.indexOf(currentStep) >= index
                    ? 'bg-gradient-to-r from-purple-500 to-pink-500'
                    : 'bg-white/10'
                }`}
              />
            ))}
          </div>
          <div className="flex justify-between text-xs text-slate-400">
            <span>Приветствие</span>
            <span>Выбор темы</span>
            <span>Настройка</span>
            <span>Готово</span>
          </div>
        </div>

        {/* Content */}
        <AnimatePresence mode="wait">
          {/* Step 1: Welcome */}
          {currentStep === 'welcome' && (
            <motion.div
              key="welcome"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="bg-white/5 backdrop-blur-xl rounded-3xl border border-white/10 p-12 text-center"
            >
              <div className="mb-8 flex justify-center">
                <div className="w-20 h-20 bg-gradient-to-br from-purple-400 to-pink-500 rounded-2xl flex items-center justify-center">
                  <Newspaper className="w-10 h-10 text-white" />
                </div>
              </div>
              
              <h1 className="text-4xl font-bold text-white mb-4">
                Добро пожаловать!
              </h1>
              <p className="text-xl text-slate-300 mb-8 max-w-2xl mx-auto leading-relaxed">
                Персональный агрегатор новостей создаст для вас идеальную ленту, 
                которая будет учиться на ваших предпочтениях.
              </p>
              <p className="text-slate-400 mb-12">
                Это займет всего <strong className="text-purple-300">1 минуту</strong>
              </p>
              
              <button
                onClick={() => setCurrentStep('presets')}
                className="inline-flex items-center gap-3 bg-gradient-to-r from-purple-500 to-pink-500 text-white px-8 py-4 rounded-xl text-lg font-semibold hover:from-purple-600 hover:to-pink-600 transition-all transform hover:scale-105"
              >
                Начать
                <ArrowRight className="w-5 h-5" />
              </button>
            </motion.div>
          )}

          {/* Step 2: Presets */}
          {currentStep === 'presets' && (
            <motion.div
              key="presets"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="bg-white/5 backdrop-blur-xl rounded-3xl border border-white/10 p-12"
            >
              <h2 className="text-3xl font-bold text-white mb-3 text-center">
                Что вас интересует?
              </h2>
              <p className="text-slate-400 mb-8 text-center leading-relaxed">
                Выберите готовый набор настроек или создайте свой на следующем шаге
              </p>

              <div className="grid md:grid-cols-2 gap-4 mb-8">
                {presets.map((preset) => (
                  <button
                    key={preset.preset_key}
                    onClick={() => handlePresetSelect(preset)}
                    className={`text-left p-6 rounded-2xl border-2 transition-all ${
                      selectedPreset?.preset_key === preset.preset_key
                        ? 'border-purple-500 bg-purple-500/20'
                        : 'border-white/10 bg-white/5 hover:border-purple-500/50'
                    }`}
                  >
                    <div className="flex items-start justify-between mb-3">
                      <div className="text-4xl mb-2">{preset.emoji}</div>
                      {selectedPreset?.preset_key === preset.preset_key && (
                        <div className="w-6 h-6 bg-purple-500 rounded-full flex items-center justify-center">
                          <Check className="w-4 h-4 text-white" />
                        </div>
                      )}
                    </div>
                    <h3 className="text-xl font-bold text-white mb-2">{preset.name}</h3>
                    <p className="text-sm text-slate-400 mb-4">{preset.description}</p>
                    <div className="flex flex-wrap gap-2">
                      {preset.categories.slice(0, 3).map((cat) => (
                        <span key={cat} className="text-xs bg-purple-500/20 text-purple-300 px-2 py-1 rounded-full">
                          {cat}
                        </span>
                      ))}
                    </div>
                  </button>
                ))}
              </div>

              <div className="flex justify-between">
                <button
                  onClick={() => setCurrentStep('welcome')}
                  className="flex items-center gap-2 text-slate-400 hover:text-white transition-colors"
                >
                  <ArrowLeft className="w-4 h-4" />
                  Назад
                </button>
                <button
                  onClick={() => setCurrentStep('customize')}
                  disabled={!canProceedToCustomize}
                  className="flex items-center gap-2 bg-gradient-to-r from-purple-500 to-pink-500 text-white px-6 py-3 rounded-xl font-semibold hover:from-purple-600 hover:to-pink-600 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Продолжить
                  <ArrowRight className="w-4 h-4" />
                </button>
              </div>
            </motion.div>
          )}

          {/* Step 3: Customize */}
          {currentStep === 'customize' && (
            <motion.div
              key="customize"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="bg-white/5 backdrop-blur-xl rounded-3xl border border-white/10 p-12"
            >
              <h2 className="text-3xl font-bold text-white mb-3 text-center">
                Настройте под себя
              </h2>
              <p className="text-slate-400 mb-8 text-center leading-relaxed">
                Добавьте или измените ключевые слова для фильтрации новостей
              </p>

              {/* Selected Preset Info */}
              {selectedPreset && (
                <div className="bg-purple-500/20 border border-purple-500/40 rounded-2xl p-4 mb-6">
                  <div className="flex items-center gap-3">
                    <span className="text-3xl">{selectedPreset.emoji}</span>
                    <div>
                      <h3 className="text-white font-semibold">{selectedPreset.name}</h3>
                      <p className="text-sm text-slate-300">{selectedPreset.description}</p>
                    </div>
                  </div>
                </div>
              )}

              {/* Keywords */}
              <div className="mb-6">
                <h3 className="text-white font-semibold mb-3">Ключевые слова:</h3>
                <div className="flex gap-2 mb-3">
                  <input
                    type="text"
                    value={newKeyword}
                    onChange={(e) => setNewKeyword(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleAddKeyword()}
                    placeholder="Добавить ключевое слово"
                    className="flex-1 bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-slate-500 focus:border-purple-500 focus:outline-none"
                  />
                  <button
                    onClick={handleAddKeyword}
                    className="bg-purple-500 hover:bg-purple-600 text-white px-6 py-3 rounded-xl font-semibold transition-colors"
                  >
                    <Plus className="w-5 h-5" />
                  </button>
                </div>
                <div className="flex flex-wrap gap-2">
                  {selectedKeywords.map((keyword) => (
                    <div
                      key={keyword}
                      className="flex items-center gap-2 bg-purple-500/20 text-purple-300 px-3 py-2 rounded-full"
                    >
                      {keyword}
                      <button
                        onClick={() => handleRemoveKeyword(keyword)}
                        className="hover:text-white transition-colors"
                      >
                        <X className="w-4 h-4" />
                      </button>
                    </div>
                  ))}
                </div>
              </div>

              {/* Categories */}
              <div className="mb-6">
                <h3 className="text-white font-semibold mb-3">Категории:</h3>
                <div className="flex flex-wrap gap-2">
                  {selectedCategories.map((category) => (
                    <span
                      key={category}
                      className="bg-pink-500/20 text-pink-300 px-3 py-2 rounded-full text-sm"
                    >
                      {category}
                    </span>
                  ))}
                </div>
              </div>

              {/* Sources Count */}
              <div className="bg-white/5 border border-white/10 rounded-xl p-4 mb-8">
                <div className="flex items-center justify-between">
                  <span className="text-slate-300">Источников новостей:</span>
                  <span className="text-2xl font-bold text-purple-400">{selectedSources.length}</span>
                </div>
              </div>

              <div className="flex justify-between">
                <button
                  onClick={() => setCurrentStep('presets')}
                  className="flex items-center gap-2 text-slate-400 hover:text-white transition-colors"
                >
                  <ArrowLeft className="w-4 h-4" />
                  Назад
                </button>
                <button
                  onClick={() => setCurrentStep('complete')}
                  disabled={!canComplete}
                  className="flex items-center gap-2 bg-gradient-to-r from-purple-500 to-pink-500 text-white px-6 py-3 rounded-xl font-semibold hover:from-purple-600 hover:to-pink-600 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Завершить
                  <ArrowRight className="w-4 h-4" />
                </button>
              </div>
            </motion.div>
          )}

          {/* Step 4: Complete */}
          {currentStep === 'complete' && (
            <motion.div
              key="complete"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="bg-white/5 backdrop-blur-xl rounded-3xl border border-white/10 p-12 text-center"
            >
              <div className="mb-8 flex justify-center">
                <motion.div
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ type: 'spring', duration: 0.5 }}
                  className="w-20 h-20 bg-gradient-to-br from-green-400 to-emerald-500 rounded-full flex items-center justify-center"
                >
                  <Sparkles className="w-10 h-10 text-white" />
                </motion.div>
              </div>
              
              <h1 className="text-4xl font-bold text-white mb-4">
                Готово!
              </h1>
              <p className="text-xl text-slate-300 mb-8 max-w-2xl mx-auto leading-relaxed">
                Мы подготовили вашу персональную новостную ленту
              </p>

              <div className="bg-white/5 border border-white/10 rounded-2xl p-6 mb-8 max-w-md mx-auto">
                <div className="grid grid-cols-3 gap-4 text-center">
                  <div>
                    <div className="text-3xl font-bold text-purple-400">{selectedKeywords.length}</div>
                    <div className="text-xs text-slate-400">Ключевых слов</div>
                  </div>
                  <div>
                    <div className="text-3xl font-bold text-pink-400">{selectedCategories.length}</div>
                    <div className="text-xs text-slate-400">Категорий</div>
                  </div>
                  <div>
                    <div className="text-3xl font-bold text-indigo-400">{selectedSources.length}</div>
                    <div className="text-xs text-slate-400">Источников</div>
                  </div>
                </div>
              </div>

              <p className="text-sm text-slate-400 mb-8 leading-relaxed">
                <strong className="text-purple-300">Подсказка:</strong> Лайкайте интересные новости, и система будет подбирать для вас похожий контент!
              </p>
              
              <button
                onClick={handleComplete}
                disabled={isLoading}
                className="inline-flex items-center gap-3 bg-gradient-to-r from-purple-500 to-pink-500 text-white px-8 py-4 rounded-xl text-lg font-semibold hover:from-purple-600 hover:to-pink-600 transition-all transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoading ? (
                  <>
                    <div className="w-5 h-5 border-2 border-white/20 border-t-white rounded-full animate-spin" />
                    Загрузка ленты...
                  </>
                ) : (
                  <>
                    Открыть мою ленту
                    <ArrowRight className="w-5 h-5" />
                  </>
                )}
              </button>
            </motion.div>
          )}
        </AnimatePresence>
        </div>
      </div>
    </div>
  );
}

