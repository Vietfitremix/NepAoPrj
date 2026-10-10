import type { Preferences, QuizAnswer, Recommendation, Weather } from '../types';
import { quizColorCodes, quizContext } from './stylistQuiz.ts';

/** Send real answers only. Defaults used by the API must not become claims in the prompt. */
export function recommendationRequest(preferences: Preferences) {
  const answers = preferences.answers || {};
  const context = Object.fromEntries(['occasion', 'style', 'weather', 'setting', 'timeOfDay', 'role', 'gender']
    .flatMap(key => typeof answers[key]?.value === 'string' && answers[key].value
      ? [[key, answers[key].value]] : []));
  const preferredColors = Array.isArray(answers.colors?.value)
    ? answers.colors.value.map(value => quizColorCodes[value]).filter(Boolean) : [];
  const prompt = [preferences.prompt.trim(), quizContext(answers)].filter(Boolean).join('. ').slice(0, 2000);
  return { prompt: prompt || 'Gợi ý Việt phục phù hợp', city: preferences.city,
    eventCode: preferences.eventCode, styleCode: preferences.styleCode,
    context: { ...context, ...(preferredColors.length ? { preferredColors } : {}) },
    ...(answers.gender?.value ? { character: preferences.character } : {}) };
}

export function resolvedPreferences(preferences: Preferences, recommendation: Recommendation): Preferences {
  return { ...preferences, eventCode: recommendation.eventCode || preferences.eventCode,
    styleCode: recommendation.styleCode || preferences.styleCode,
    character: recommendation.character || preferences.character,
    weather: recommendation.weather || preferences.weather };
}

/** Merge context for scoring without turning AI inference into explicit quiz choices next time. */
export function contextualAnswers(preferences?: Preferences, recommendation?: Recommendation): Record<string, QuizAnswer> {
  const answers: Record<string, QuizAnswer> = { ...preferences?.answers };
  for (const key of ['weather', 'setting', 'timeOfDay', 'role']) {
    const value = recommendation?.context?.[key];
    if (typeof value === 'string' && !answers[key]?.value) answers[key] = { ...answers[key], value };
  }
  return answers;
}

export interface RecommendationAnalysis {
  event: string; weather: Weather; styles: string[]; understanding: string;
  character?: Preferences['character']; context?: Record<string, unknown>; source?: 'gemini' | 'fallback';
}
