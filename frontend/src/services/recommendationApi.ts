import { api } from './api';
import type { Preferences, Recommendation } from '../types';
import { previewFor } from './backendContract';
import type { ReferenceData } from './backendContract';
import { recommendationRequest } from '../utils/recommendationContext';
import type { RecommendationAnalysis } from '../utils/recommendationContext';
interface Response {
  analysis: RecommendationAnalysis;
  concepts: { conceptName: string; outfitCode: string; colorCode: string; styleCode: string;
    accessories: string[]; matchScore: number; reason: string }[];
}
export async function recommend(preferences: Preferences): Promise<Recommendation> {
  const refs = (await api.get<ReferenceData>('/reference-data')).data;
  const data = (await api.post<Response>('/recommendations', recommendationRequest(preferences), { timeout: 90000 })).data;
  const id = crypto.randomUUID();
  return { id, understanding: data.analysis.understanding || `Yêu cầu của bạn: ${preferences.prompt || 'Việt phục phù hợp'}`,
    eventCode: data.analysis.event, styleCode: data.analysis.styles[0], character: data.analysis.character,
    context: data.analysis.context, weather: data.analysis.weather,
    concepts: data.concepts.map((c, i) => ({ id: id + '-' + i, name: c.conceptName,
      outfitCode: c.outfitCode, outfitName: refs.outfits.find(d => d.outfit.code === c.outfitCode)?.outfit.name || c.outfitCode,
      imageUrl: previewFor(refs.outfits.find(d => d.outfit.code === c.outfitCode), c.colorCode),
      colorCode: c.colorCode, colorName: refs.colors.find(x => x.code === c.colorCode)?.name || c.colorCode,
      styleCode: c.styleCode, styleName: refs.styles.find(x => x.code === c.styleCode)?.name || c.styleCode,
      matchScore: c.matchScore, reason: c.reason, accessoryCodes: c.accessories })) };
}
