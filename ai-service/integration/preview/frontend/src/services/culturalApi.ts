import { api } from './api';
import { selection } from './backendContract';
import type { Summary } from './backendContract';
import type { CulturalKnowledge, CulturalResult, MixConfig } from '../types';
interface Knowledge { category: string; title: string; content: string; sourceName: string | null; sourceUrl: string | null }
export async function getCulturalKnowledge(code: string, signal?: AbortSignal): Promise<CulturalKnowledge> {
  const [knowledge, detail] = await Promise.all([
    api.get<Knowledge[]>('/outfits/' + encodeURIComponent(code) + '/cultural-knowledge', { signal }),
    api.get<{ outfit: Summary }>('/outfits/' + encodeURIComponent(code), { signal })]);
  const rows = knowledge.data, outfit = detail.data.outfit;
  const content = (category: string) => rows.filter(r => r.category === category).map(r => r.content).join(' ');
  return { name: outfit.name, origin: outfit.origin || content('ORIGIN') || 'Chưa có dữ liệu được kiểm chứng.',
    meaning: outfit.culturalMeaning || content('MEANING') || 'Chưa có dữ liệu được kiểm chứng.',
    characteristics: rows.map(r => r.title + ': ' + r.content).join(' ') || 'Chưa có dữ liệu được kiểm chứng.',
    sources: rows.filter(r => r.sourceUrl).map(r => ({ title: r.sourceName || r.title, url: r.sourceUrl! })) };
}
export const getCulturalScore = (config: MixConfig, signal?: AbortSignal) => api.post<CulturalResult>(
  '/cultural-score', selection(config), { signal }).then(r => r.data);
