import { useEffect, useState } from 'react';
import { figureSVG } from '../../ai/figure';
import type { OutfitState } from '../../ai/types';

export function useFigure(s: OutfitState | null | undefined, view = 'truoc') {
  const [r, setR] = useState<{ svg: string; missing: string[] }>();
  const key = JSON.stringify([s, view]);
  useEffect(() => { let live = true; if (s) figureSVG(s, view).then(x => { if (live) setR(x); }); return () => { live = false; }; /* eslint-disable-next-line */ }, [key]);
  return r;
}
export function Figure({ state, view = 'truoc', className = '' }: { state: OutfitState; view?: string; className?: string }) {
  const r = useFigure(state, view);
  return <div className={`nfigure ${className}`} role="img" aria-label="Người mẫu mặc bộ đã chọn" dangerouslySetInnerHTML={{ __html: r?.svg || '' }} />;
}
