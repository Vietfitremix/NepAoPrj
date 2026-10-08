import { useNavigate } from 'react-router-dom';
import { aiApi } from './api';
import { useStore } from './store';
import type { ClarifyResponse, Context, OutfitsResponse, OutfitState, StylistOutfit } from './types';

export const LEVEL = { ok: 'Phù hợp', consider: 'Nên cân nhắc', risk: 'Dễ gây sai lệch' } as const;
export const CTX_FIELDS = ['occasion', 'weather', 'setting', 'timeOfDay', 'role', 'style', 'gender'];
export const fullContext = (context: Context | null, s: OutfitState): Context => ({ ...(context || {}), occasion: s.occasion, style: s.style, gender: s.gender });
export const reviewKey = (context: Context | null, s: OutfitState) => JSON.stringify([s, fullContext(context, s)]);

/** Hỏi stylist: gửi câu trả lời quiz (hoặc một câu kể nhanh) → 3 bộ gợi ý. */
export function useActions() {
  const store = useStore(); const navigate = useNavigate();
  async function ask(body: Record<string, unknown>) {
    store.set({ stylist: { loading: true }, review: { key: null, res: null } }); navigate('/concepts');
    try {
      const t0 = performance.now();
      const res = await aiApi<OutfitsResponse | ClarifyResponse>('/stylist', body);
      store.set({ stylist: { res, body, ms: Math.round(performance.now() - t0) }, context: res.kind === 'outfits' ? res.intent : store.context });
    } catch (e) { store.set({ stylist: { error: e instanceof Error ? e.message : String(e), body } }); }
  }
  function open(o: StylistOutfit | OutfitState) {
    const s = 'state' in o ? o.state : o;
    store.set({ state: JSON.parse(JSON.stringify({ pattern: 'tron', ...s })), view: 'truoc', review: { key: null, res: null } });
    navigate('/mix');
  }
  return { ask, open };
}
