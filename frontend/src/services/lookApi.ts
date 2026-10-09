import { api } from './api';
import { selection, lookView } from './backendContract';
import type { SavedLook, ReferenceData } from './backendContract';
import type { MixConfig } from '../types';
import { normalizeMaleSelection } from '../utils/maleWardrobe';
import type { WardrobeCharacter } from '../utils/maleWardrobe';
interface SharedWardrobeLook { state: { lookId: number; wardrobe: NonNullable<MixConfig['wardrobe']> } }

function restoreWardrobe(look: ReturnType<typeof lookView>, id: string, wardrobe: NonNullable<MixConfig['wardrobe']>) {
  const character:WardrobeCharacter=wardrobe.character==='male'?'male':'female';
  return {...look,id,config:{...look.config,conceptId:'saved-'+id,
    wardrobe:{character,selection:normalizeMaleSelection(wardrobe.selection,character)}}};
}
export async function createLook(config: MixConfig) {
  const refs = (await api.get<ReferenceData>('/reference-data')).data;
  const data = (await api.post<SavedLook>('/looks', selection(config))).data;
  const look=lookView(data, refs);
  if (!config.wardrobe) return look;
  const shared=(await api.post<{id:string}>('/shared-looks', {state:{lookId:data.id,wardrobe:config.wardrobe}})).data;
  return restoreWardrobe(look,shared.id,config.wardrobe);
}
export async function getLook(id: string, signal?: AbortSignal) {
  if (/^[a-f0-9]{8}(?:-[a-f0-9]{4}){3}-[a-f0-9]{12}$/i.test(id)) {
    const shared=(await api.get<SharedWardrobeLook>('/shared-looks/'+encodeURIComponent(id),{signal})).data;
    if (!Number.isSafeInteger(shared.state?.lookId) || shared.state.lookId<=0 || !shared.state.wardrobe)
      throw new Error('Look này không có dữ liệu tủ đồ hợp lệ.');
    const [look,refs]=await Promise.all([api.get<SavedLook>('/looks/'+shared.state.lookId,{signal}),
      api.get<ReferenceData>('/reference-data',{signal})]);
    return restoreWardrobe(lookView(look.data,refs.data),id,shared.state.wardrobe);
  }
  const [look, refs] = await Promise.all([api.get<SavedLook>('/looks/' + encodeURIComponent(id), { signal }),
    api.get<ReferenceData>('/reference-data', { signal })]);
  return lookView(look.data, refs.data);
}
