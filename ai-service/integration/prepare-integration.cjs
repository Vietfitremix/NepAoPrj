// Creates a reviewable patch; does not modify the protected backend/frontend files.
const fs = require('node:fs');
const path = require('node:path');
const changes = new Map();
function replace(file, before, after) {
  const text = changes.get(file) ?? fs.readFileSync(file, 'utf8').replace(/\r\n/g, '\n');
  if (!text.includes(before)) throw new Error(`Missing patch anchor: ${file}`);
  changes.set(file, text.replaceAll(before, after));
}
replace('backend/src/main/java/com/vietphuc/remix/client/AiClient.java', '"/recommendations"', '"/ai/recommendations"');
replace('backend/src/main/java/com/vietphuc/remix/client/AiClient.java', '"/remix"', '"/ai/remix"');
replace('backend/src/test/java/com/vietphuc/remix/ClientContractTest.java', '"/recommendations"', '"/ai/recommendations"');
replace('backend/src/test/java/com/vietphuc/remix/ClientContractTest.java', '"/remix"', '"/ai/remix"');
replace('backend/docker-compose.yml', 'build: ./ai-service', 'build: ../ai-service');
replace('backend/docker-compose.yml', 'GEMINI_API_KEY: ${GEMINI_API_KEY:-}', 'BACKEND_COMPAT_ONLY: "true"\n      ENABLE_DEV_ROUTES: "false"\n      GEMINI_API_KEY: ${GEMINI_API_KEY:-}');
replace('backend/docker-compose.yml', 'GEMINI_MODEL: ${GEMINI_MODEL:-}', 'GEMINI_MODEL: ${GEMINI_MODEL:-gemini-flash-latest}');
replace('backend/docker-compose.yml', 'build: .\n', 'build: .\n    ports:\n      - "127.0.0.1:8080:8080"\n');
replace('frontend/src/services/api.ts', 'timeout: 30000', 'timeout: 65000');
changes.set('frontend/src/services/backendContract.ts', `import type { MixConfig, Outfit, Look, Option } from '../types';
export interface Ref { code: string; name: string; description?: string }
export interface Summary extends Ref { thumbnailUrl: string | null; origin?: string; culturalMeaning?: string }
export interface Detail {
  outfit: Summary;
  colors: { code: string; name: string; hexCode: string }[];
  assets: { colorCode: string | null; assetType: string; variantCode: string | null; imageUrl: string; layerOrder: number }[];
  accessories: { code: string; name: string; imageUrl: string | null; layerOrder: number | null }[];
}
export interface ReferenceData { outfits: Detail[]; colors: Detail['colors']; styles: Ref[]; events: Ref[] }
export interface SavedLook {
  id: number; outfitCode: string; colorCode: string; styleCode: string; eventCode: string;
  accessories: string[]; styleMatchScore: number | null; culturalScore: number | null;
  colorHarmonyScore: number | null; previewImageUrl: string | null;
}
export const selection = (config: MixConfig) => ({ outfitCode: config.outfitCode, colorCode: config.colorCode,
  styleCode: config.styleCode, eventCode: config.eventCode, accessories: config.accessoryCodes });
export const options = (rows: Ref[]): Option[] => rows.map(r => ({ code: r.code, label: r.name }));
export const previewFor = (detail: Detail | undefined, color: string) => {
  const layer = detail?.assets.find(a => a.colorCode === color && a.assetType === 'GARMENT')?.imageUrl;
  return layer?.endsWith('-layer.svg') ? layer.replace('-layer.svg', '.svg') : detail?.outfit.thumbnailUrl || '';
};
export function outfitView(detail: Detail, styles: Ref[]): Outfit {
  return { code: detail.outfit.code, name: detail.outfit.name,
    baseAvatarUrl: detail.assets.find(a => a.assetType === 'BASE_AVATAR')?.imageUrl || '',
    assets: detail.assets.filter(a => a.assetType !== 'BASE_AVATAR').map((a, i) => ({ id: String(i),
      url: a.imageUrl, colorCode: a.colorCode || undefined, zIndex: a.layerOrder })),
    colors: detail.colors.map(c => ({ code: c.code, label: c.name, hex: c.hexCode })), styles: options(styles),
    accessories: detail.accessories.map(a => ({ code: a.code, label: a.name, assetUrl: a.imageUrl || '', zIndex: a.layerOrder ?? undefined })) };
}
export function lookView(data: SavedLook, refs: ReferenceData): Look {
  const outfit = refs.outfits.find(d => d.outfit.code === data.outfitCode)?.outfit;
  return { id: String(data.id), name: outfit?.name || data.outfitCode,
    imageUrl: data.previewImageUrl || '', outfitCode: data.outfitCode, outfitName: outfit?.name || data.outfitCode,
    styleName: refs.styles.find(s => s.code === data.styleCode)?.name || data.styleCode,
    eventName: refs.events.find(e => e.code === data.eventCode)?.name || data.eventCode,
    matchScore: data.styleMatchScore, culturalScore: data.culturalScore, colorHarmony: data.colorHarmonyScore,
    config: { conceptId: 'saved-' + data.id, outfitCode: data.outfitCode, colorCode: data.colorCode,
      styleCode: data.styleCode, eventCode: data.eventCode, accessoryCodes: data.accessories } };
}
`);
changes.set('frontend/src/services/recommendationApi.ts', `import { api } from './api';
import type { Preferences, Recommendation } from '../types';
import { previewFor } from './backendContract';
import type { ReferenceData } from './backendContract';
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
  const prompt = [preferences.prompt.trim(), 'Dịp: ' + event, 'Phong cách: ' + style, color ? 'Màu ' + color : ''].filter(Boolean).join('. ');
  const data = (await api.post<Response>('/recommendations', { prompt, city: preferences.city,
    eventCode: preferences.eventCode, styleCode: preferences.styleCode })).data;
  const id = crypto.randomUUID();
  return { id, understanding: event + ' · ' + preferences.city + ' · ' + data.analysis.weather.temperature + '°C · ' + style,
    concepts: data.concepts.map((c, i) => ({ id: id + '-' + i, name: c.conceptName,
      outfitCode: c.outfitCode, outfitName: refs.outfits.find(d => d.outfit.code === c.outfitCode)?.outfit.name || c.outfitCode,
      imageUrl: previewFor(refs.outfits.find(d => d.outfit.code === c.outfitCode), c.colorCode),
      colorCode: c.colorCode, colorName: refs.colors.find(x => x.code === c.colorCode)?.name || c.colorCode,
      styleCode: c.styleCode, styleName: refs.styles.find(x => x.code === c.styleCode)?.name || c.styleCode,
      matchScore: c.matchScore, reason: c.reason, accessoryCodes: c.accessories })) };
}
`);
changes.set('frontend/src/services/outfitApi.ts', `import { api } from './api';
import { outfitView } from './backendContract';
import type { Detail, ReferenceData } from './backendContract';
export const getOutfits = async () => {
  const refs = (await api.get<ReferenceData>('/reference-data')).data;
  return refs.outfits.map(d => outfitView(d, refs.styles));
};
export async function getOutfit(code: string, signal?: AbortSignal) {
  const [detail, refs] = await Promise.all([
    api.get<Detail>('/outfits/' + encodeURIComponent(code), { signal }),
    api.get<ReferenceData>('/reference-data', { signal })]);
  return outfitView(detail.data, refs.data.styles);
}
`);
changes.set('frontend/src/services/remixApi.ts', `import { api } from './api';
import type { MixConfig, RemixResult } from '../types';
import { selection } from './backendContract';
export { applyChanges } from '../utils/mix';
export const remix = (config: MixConfig, prompt: string) => api.post<RemixResult>('/remix', {
  currentLook: selection(config), prompt }).then(r => r.data);
`);
changes.set('frontend/src/services/lookApi.ts', `import { api } from './api';
import { selection, lookView } from './backendContract';
import type { SavedLook, ReferenceData } from './backendContract';
import type { MixConfig } from '../types';
export async function createLook(config: MixConfig) {
  const refs = (await api.get<ReferenceData>('/reference-data')).data;
  const data = (await api.post<SavedLook>('/looks', selection(config))).data;
  return lookView(data, refs);
}
export async function getLook(id: string, signal?: AbortSignal) {
  const [look, refs] = await Promise.all([api.get<SavedLook>('/looks/' + encodeURIComponent(id), { signal }),
    api.get<ReferenceData>('/reference-data', { signal })]);
  return lookView(look.data, refs.data);
}
`);
changes.set('frontend/src/services/culturalApi.ts', `import { api } from './api';
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
`);
replace('frontend/src/types/index.ts', 'export interface CulturalResult { score: number;', 'export interface CulturalResult { score: number | null;');
replace('frontend/src/types/index.ts', 'matchScore: number; culturalScore: number; colorHarmony: number;', 'matchScore: number | null; culturalScore: number | null; colorHarmony: number | null;');
replace('frontend/src/components/cultural/CulturalScore.tsx', "SAFE: 'Hài hòa với văn hóa'", "INSUFFICIENT_DATA: 'Chưa đủ dữ liệu văn hóa', WELL_PRESERVED: 'Giữ gìn tốt', SUITABLE: 'Phù hợp', SAFE: 'Hài hòa với văn hóa'");
replace('frontend/src/components/cultural/CulturalScore.tsx', 'Math.min(100,result.score)', 'Math.min(100,result.score ?? 0)');
replace('frontend/src/components/cultural/CulturalScore.tsx', '<strong>{result.score}<small>%</small></strong>', "<strong>{result.score ?? '—'}{result.score !== null && <small>%</small>}</strong>");
replace('frontend/src/components/cultural/CulturalScore.tsx', 'Máy chủ không ghi nhận cảnh báo cho bản phối này.', "{result.score === null ? 'Chưa đủ quy tắc được kiểm chứng để kết luận về bản phối.' : 'Máy chủ không ghi nhận cảnh báo cho bản phối này.'}");
changes.set('frontend/src/components/mix/SavedLookPreview.tsx', `import { useEffect, useState } from 'react';
import type { MixConfig, Outfit } from '../../types';
import { getOutfit } from '../../services/outfitApi';
import { errorMessage } from '../../services/api';
import { ErrorBox, Loading } from '../common/UI';
import Avatar2D from './Avatar2D';
export default function SavedLookPreview({ config }: { config: MixConfig }) {
  const [outfit, setOutfit] = useState<Outfit>();
  const [error, setError] = useState('');
  useEffect(() => { const controller = new AbortController(); setOutfit(undefined); setError('');
    getOutfit(config.outfitCode, controller.signal).then(o => { if (!controller.signal.aborted) setOutfit(o); })
      .catch(e => { if (!controller.signal.aborted) setError(errorMessage(e)); });
    return () => controller.abort(); }, [config.outfitCode]);
  return error ? <ErrorBox message={error}/> : outfit ? <Avatar2D outfit={outfit} config={config}/> : <Loading text="Đang tải bản phối 2D…"/>;
}
`);
replace('frontend/src/pages/FinalLookPage.tsx', "import { getLook } from '../services/lookApi';", "import { getLook } from '../services/lookApi';\nimport SavedLookPreview from '../components/mix/SavedLookPreview';");
replace('frontend/src/pages/FinalLookPage.tsx', '<img src={look.imageUrl} alt={`Final look: ${look.name}`}/>', '<SavedLookPreview config={look.config}/>');
replace('frontend/src/pages/FinalLookPage.tsx', '{value}%', "{value === null ? 'Chưa có dữ liệu' : value + '%'}");
replace('frontend/src/pages/StylistPage.tsx', "CLEAR: 'Trời quang', CLOUDY:", "CLEAR: 'Trời quang', CLOUDS: 'Nhiều mây', CLOUDY:");
changes.set('backend/src/main/resources/db/migration/V3__figure_assets.sql', fs.readFileSync('frontend/tools/V3__figure_assets.sql', 'utf8'));
replace('backend/README.md', 'cd ai-service', 'cd ../ai-service');
replace('backend/README.md', 'uvicorn app:app', 'uvicorn app.main:app');
replace('backend/README.md', "$env:GEMINI_API_KEY = 'your-gemini-key'", "$env:BACKEND_COMPAT_ONLY = 'true'\n$env:GEMINI_API_KEY = 'your-gemini-key'");
replace('backend/README.md', 'Nếu thiếu Gemini key/model, AI service trả 503\nvà backend báo lỗi upstream, không tạo concept giả.', 'AI service bên ngoài có nhánh dự phòng khi thiếu Gemini key; backend vẫn kiểm tra mã và đúng 3 concept.');
for (const file of ['backend/ai-service/app.py', 'backend/ai-service/Dockerfile', 'backend/ai-service/requirements.txt']) changes.set(file, null);
let patch = '';
const staging = path.resolve('ai-service/integration/preview');
for (const [file, result] of changes) {
  const exists = fs.existsSync(file);
  const before = exists ? fs.readFileSync(file, 'utf8').replace(/\r\n/g, '\n') : '';
  const after = result === null ? '' : result.replace(/\r\n/g, '\n');
  if (after === before) continue;
  const lines = s => s ? s.replace(/\n$/, '').split('\n') : [];
  const oldLines = lines(before), newLines = lines(after);
  patch += 'diff --git a/' + file + ' b/' + file + '\n';
  if (!exists) patch += 'new file mode 100644\n';
  if (result === null) patch += 'deleted file mode 100644\n';
  patch += '--- ' + (exists ? 'a/' + file : '/dev/null') + '\n+++ ' + (result === null ? '/dev/null' : 'b/' + file) + '\n';
  patch += '@@ -' + (oldLines.length ? '1,' + oldLines.length : '0,0') + ' +' + (newLines.length ? '1,' + newLines.length : '0,0') + ' @@\n';
  patch += oldLines.map(l => '-' + l + '\n').join('') + newLines.map(l => '+' + l + '\n').join('');
  if (result !== null) {
    const target = path.join(staging, file);
    fs.mkdirSync(path.dirname(target), { recursive: true });
    fs.writeFileSync(target, after);
  }
}
fs.writeFileSync('ai-service/integration/integration.patch', patch);
console.log('Prepared ai-service/integration/integration.patch and ' + changes.size + ' reviewable file changes.');
