import { api } from './api';
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
