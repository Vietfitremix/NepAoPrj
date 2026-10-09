import { api } from './api';
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
