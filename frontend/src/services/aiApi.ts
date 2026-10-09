import { selection } from './backendContract';
import type { MixConfig, QuizAnswer } from '../types';
import type { ChecklistTips, CultureCardData, ReviewNote, ScoreCardData } from '../utils/lookbook';
import { getWardrobe, normalizeMaleSelection, selectedWardrobeItems } from '../utils/maleWardrobe';
import type { MaleSelection, WardrobeCharacter } from '../utils/maleWardrobe';
import { reviewContext } from '../utils/outfitContext';
export { reviewContext } from '../utils/outfitContext';

export interface WardrobeReview {
  verdict: 'hop' | 'nen_chinh' | 'chua_hop'; verdictText: string; source: string;
  current: { title: string; comment: string; tip: string; scoreCard?: ScoreCardData | null; color?: { score: number; note: string } };
}
async function aiFetch<T>(path: string, body?: unknown, signal?: AbortSignal): Promise<T> {
  const r = await fetch('/ai' + path, body ? { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body), signal } : { signal });
  if (!r.ok) throw new Error(r.status === 429 ? 'Có nhiều yêu cầu cùng lúc. Bạn hãy thử lại sau ít giây.' : 'Stylist chưa thể nhận xét lúc này. Vui lòng thử lại.');
  return r.json() as Promise<T>;
}
/** Bối cảnh từ bộ câu hỏi (thời tiết, nơi mặc, buổi, vai trò) để lời nhận xét bám đúng hoàn cảnh. */
export function wardrobeReview(config: MixConfig, answers?: Record<string, QuizAnswer>, signal?: AbortSignal) {
  const w = config.wardrobe;
  const names = w ? Object.fromEntries(selectedWardrobeItems(normalizeMaleSelection(w.selection, w.character), w.character).map(i => [i.id, i.name])) : {};
  return aiFetch<WardrobeReview>('/wardrobe-review', { ...selection(config), context: reviewContext(answers), names }, signal);
}
export async function lookbookExtras(signal?: AbortSignal): Promise<{ tips: ChecklistTips; cultureCards: CultureCardData[] }> {
  const c = await aiFetch<{ checklist?: ChecklistTips; cultureCards?: CultureCardData[] }>('/catalog', undefined, signal);
  return { tips: c.checklist || {}, cultureCards: c.cultureCards || [] };
}
export const noteOf = (r?: WardrobeReview | null): ReviewNote => ({ title: r?.current.title || '', comment: r?.current.comment || '', tip: r?.current.tip || '', card: r?.current.scoreCard });

export interface RemixOption { label: string; score: number; band: string; why: string; selection: MaleSelection }
export interface WardrobeRemix {
  status: 'hop' | 'dieu_chinh' | 'khong_hop' | 'chua_ro'; applied: boolean; analysis: string; explanation: string; source: string;
  scoreBefore: number; scoreRequested: number; scoreAfter: number; selection: MaleSelection; options: RemixOption[];
}
/** AI Remix: phân tích bối cảnh, nói thẳng yêu cầu có hợp không và đưa lựa chọn phù hợp hơn (xem /ai/wardrobe-remix). */
export function wardrobeRemix(config: MixConfig, prompt: string, answers?: Record<string, QuizAnswer>, signal?: AbortSignal) {
  const character: WardrobeCharacter = config.wardrobe?.character || 'female';
  const w = getWardrobe(character);
  const pick = (list: { id: string; name: string; slot?: string }[]) => list.map(i => ({ id: i.id, name: i.name, ...(i.slot ? { slot: i.slot } : {}) }));
  return aiFetch<WardrobeRemix>('/wardrobe-remix', { ...selection(config), prompt, context: reviewContext(answers),
    options: { outfits: pick(w.outfits), pants: pick(w.pants), shoes: pick(w.shoes), accessories: pick(w.accessories) } }, signal);
}
