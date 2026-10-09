import { selection } from './backendContract';
import type { MixConfig, QuizAnswer } from '../types';
import type { ChecklistTips, CultureCardData, ReviewNote, ScoreCardData } from '../utils/lookbook';

export interface WardrobeReview {
  verdict: 'hop' | 'nen_chinh'; verdictText: string; source: string;
  current: { title: string; comment: string; tip: string; scoreCard?: ScoreCardData | null };
}
async function aiFetch<T>(path: string, body?: unknown, signal?: AbortSignal): Promise<T> {
  const r = await fetch('/ai' + path, body ? { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body), signal } : { signal });
  if (!r.ok) throw new Error(r.status === 429 ? 'Có nhiều yêu cầu cùng lúc. Bạn hãy thử lại sau ít giây.' : 'Stylist chưa thể nhận xét lúc này. Vui lòng thử lại.');
  return r.json() as Promise<T>;
}
/** Bối cảnh từ bộ câu hỏi (thời tiết, nơi mặc, buổi, vai trò) để lời nhận xét bám đúng hoàn cảnh. */
export function reviewContext(answers?: Record<string, QuizAnswer>) {
  const pick = (id: string) => { const v = answers?.[id]?.value; return typeof v === 'string' ? v : undefined; };
  return Object.fromEntries(Object.entries({ weather: pick('weather'), setting: pick('setting'), timeOfDay: pick('timeOfDay'), role: pick('role') }).filter(([, v]) => v));
}
export const wardrobeReview = (config: MixConfig, answers?: Record<string, QuizAnswer>, signal?: AbortSignal) =>
  aiFetch<WardrobeReview>('/wardrobe-review', { ...selection(config), context: reviewContext(answers) }, signal);
export async function lookbookExtras(signal?: AbortSignal): Promise<{ tips: ChecklistTips; cultureCards: CultureCardData[] }> {
  const c = await aiFetch<{ checklist?: ChecklistTips; cultureCards?: CultureCardData[] }>('/catalog', undefined, signal);
  return { tips: c.checklist || {}, cultureCards: c.cultureCards || [] };
}
export const noteOf = (r?: WardrobeReview | null): ReviewNote => ({ title: r?.current.title || '', comment: r?.current.comment || '', tip: r?.current.tip || '', card: r?.current.scoreCard });
