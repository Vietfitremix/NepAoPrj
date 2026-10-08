import { createContext, useCallback, useContext, useEffect, useRef, useState } from 'react';
import type { ReactNode } from 'react';
import { aiApi } from './api';
import { motif, setCatalog } from './figure';
import type { Answer, Catalog, Context, OutfitState, QuizQuestion, RawCatalog, ReviewResponse, StylistResult } from './types';

const byId = <T extends { id: string }>(list: T[]) => Object.fromEntries(list.map(x => [x.id, x])) as Record<string, T>;
const KEY = 'nepao-session-v1';

export interface Saved {
  answers: Record<string, Answer>; step: number; context: Context | null; stylist: StylistResult | null;
  state: OutfitState | null; view: string; review: { key: string | null; res: ReviewResponse | null };
}
const EMPTY: Saved = { answers: {}, step: 0, context: null, stylist: null, state: null, view: 'truoc', review: { key: null, res: null } };
function read(): Saved {
  try { return { ...EMPTY, ...(JSON.parse(sessionStorage.getItem(KEY) || '{}') as Partial<Saved>) }; } catch { return EMPTY; }
}

interface Store extends Saved {
  catalog: Catalog | null; quiz: QuizQuestion[]; loadError: string; loading: boolean;
  set: (patch: Partial<Saved>) => void; reset: () => void; reload: () => void;
}
const Ctx = createContext<Store>(null as unknown as Store);
export const useStore = () => useContext(Ctx);

export function StoreProvider({ children }: { children: ReactNode }) {
  const [saved, setSaved] = useState<Saved>(read);
  const [catalog, setCat] = useState<Catalog | null>(null);
  const [quiz, setQuiz] = useState<QuizQuestion[]>([]);
  const [loadError, setLoadError] = useState('');
  const [loading, setLoading] = useState(true);
  const [tick, setTick] = useState(0);
  const first = useRef(true);

  useEffect(() => {
    const ctl = new AbortController();
    setLoading(true); setLoadError('');
    Promise.all([aiApi<RawCatalog>('/catalog', undefined, ctl.signal), aiApi<QuizQuestion[]>('/quiz', undefined, ctl.signal)]).then(async ([cat, q]) => {
      const full: Catalog = { ...cat, color: byId(cat.colors), acc: byId(cat.accessories), garment: byId(cat.garments), pattern: byId(cat.patterns), occasion: byId(cat.occasions), style: byId(cat.styles) };
      setCatalog(full);
      await Promise.all(cat.patterns.filter(p => p.kind === 'placement').map(p => motif(p.id)));
      setCat(full); setQuiz(q); setLoading(false);
    }).catch(e => { if (!ctl.signal.aborted) { setLoadError(e instanceof Error ? e.message : String(e)); setLoading(false); } });
    return () => ctl.abort();
  }, [tick]);

  const set = useCallback((patch: Partial<Saved>) => setSaved(prev => ({ ...prev, ...patch })), []);
  const reset = useCallback(() => setSaved(EMPTY), []);
  useEffect(() => {
    if (first.current) { first.current = false; return; }
    try { sessionStorage.setItem(KEY, JSON.stringify({ ...saved, stylist: saved.stylist?.error ? null : saved.stylist })); } catch { /* lưu phiên không bắt buộc */ }
  }, [saved]);

  return <Ctx.Provider value={{ ...saved, catalog, quiz, loadError, loading, set, reset, reload: () => setTick(t => t + 1) }}>{children}</Ctx.Provider>;
}
