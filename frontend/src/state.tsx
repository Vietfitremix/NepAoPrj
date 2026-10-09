import { createContext, useContext, useState } from 'react';
import type { ReactNode } from 'react';
import type { MixConfig, Preferences, Recommendation } from './types';
interface Session { preferences?: Preferences; recommendation?: Recommendation; mix?: MixConfig }
function read(): Session {
  try {
    const value: unknown = JSON.parse(sessionStorage.getItem('viet-fit-session') || '{}');
    return value && typeof value === 'object' && !Array.isArray(value) ? value as Session : {};
  } catch { return {}; }
}
const Context = createContext<{ session: Session; update: (value: Partial<Session>) => void }>({ session: {}, update: () => {} });
export function SessionProvider({ children }: { children: ReactNode }) {
  const [session, setSession] = useState<Session>(read);
  function update(value: Partial<Session>) { setSession(prev => { const next = { ...prev, ...value }; try { sessionStorage.setItem('viet-fit-session', JSON.stringify(next)); } catch { /* Continue in memory when storage is unavailable. */ } return next; }); }
  return <Context.Provider value={{ session, update }}>{children}</Context.Provider>;
}
export const useSession = () => useContext(Context);
