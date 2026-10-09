import { api } from './api';
import { selection } from './backendContract';
import type { Summary } from './backendContract';
import type { CulturalKnowledge, CulturalResult, MixConfig } from '../types';
import { culturalKnowledge } from '../utils/culturalKnowledge';
import type { KnowledgeRow } from '../utils/culturalKnowledge';
export async function getCulturalKnowledge(code: string, signal?: AbortSignal): Promise<CulturalKnowledge> {
  const [knowledge, detail] = await Promise.all([
    api.get<KnowledgeRow[]>('/outfits/' + encodeURIComponent(code) + '/cultural-knowledge', { signal }),
    api.get<{ outfit: Summary }>('/outfits/' + encodeURIComponent(code), { signal })]);
  return culturalKnowledge(knowledge.data, detail.data.outfit);
}
export const getCulturalScore = (config: MixConfig, signal?: AbortSignal) => api.post<CulturalResult>(
  '/cultural-score', selection(config), { signal }).then(r => r.data);
