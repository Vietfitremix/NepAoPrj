import { api } from './api';
import type { Preferences, Recommendation } from '../types';
import { previewFor } from './backendContract';
import type { ReferenceData } from './backendContract';
import { quizContext } from '../utils/stylistQuiz';
interface Response {
  analysis: { event: string; weather: Preferences['weather']; styles: string[] };
  concepts: { conceptName: string; outfitCode: string; colorCode: string; styleCode: string;
    accessories: string[]; matchScore: number; reason: string }[];
}
export async function recommend(preferences: Preferences): Promise<Recommendation> {
  const refs = (await api.get<ReferenceData>('/reference-data')).data;
  const color = refs.colors.find(c => c.code === preferences.colorCode)?.name;
  const event = refs.events.find(e => e.code === preferences.eventCode)?.name || preferences.eventCode;
  const style = refs.styles.find(s => s.code === preferences.styleCode)?.name || preferences.styleCode;
  const context = [preferences.answers ? quizContext(preferences.answers) : '', 'Dịp: ' + event,
    'Phong cách: ' + style, color ? 'Màu ' + color : ''].filter(Boolean).join('. ');
  const prompt = [context, preferences.prompt.trim().slice(0, Math.max(0, 1998 - context.length))].filter(Boolean).join('. ');
  const data = (await api.post<Response>('/recommendations', { prompt, city: preferences.city,
    eventCode: preferences.eventCode, styleCode: preferences.styleCode, character: preferences.character || 'female' })).data;
  const id = crypto.randomUUID();
  return { id, understanding: event + ' · ' + preferences.city + ' · ' + data.analysis.weather.temperature + '°C · ' + style,
    concepts: data.concepts.map((c, i) => ({ id: id + '-' + i, name: c.conceptName,
      outfitCode: c.outfitCode, outfitName: refs.outfits.find(d => d.outfit.code === c.outfitCode)?.outfit.name || c.outfitCode,
      imageUrl: previewFor(refs.outfits.find(d => d.outfit.code === c.outfitCode), c.colorCode),
      colorCode: c.colorCode, colorName: refs.colors.find(x => x.code === c.colorCode)?.name || c.colorCode,
      styleCode: c.styleCode, styleName: refs.styles.find(x => x.code === c.styleCode)?.name || c.styleCode,
      matchScore: c.matchScore, reason: c.reason, accessoryCodes: c.accessories })) };
}
