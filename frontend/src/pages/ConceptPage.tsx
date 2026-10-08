import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { ArrowLeft, Sparkles } from 'lucide-react';
import { EmptyState, ErrorBox, Loading, PageHeading, Stepper } from '../components/common/UI';
import OutfitCard from '../components/ai/OutfitCard';
import { CTX_FIELDS, useActions } from '../ai/actions';
import { useStore } from '../ai/store';
import type { Context } from '../ai/types';

export function useContextTags(ctx: Context | null): string[] {
  const { catalog: CAT, quiz } = useStore();
  if (!ctx || !CAT) return [];
  const lab = (f: string, v: string) => f === 'occasion' ? CAT.occasion[v]?.name : f === 'style' ? CAT.style[v]?.name : f === 'gender' ? ({ nu: 'Nữ', nam: 'Nam' } as Record<string, string>)[v]
    : quiz.find(q => q.field === f)?.options.find(o => o.value === v)?.label;
  return CTX_FIELDS.map(f => { const v = ctx[f]; return typeof v === 'string' ? (lab(f, v) || '') : ''; }).filter(Boolean);
}

/** Bước 2: stylist gợi ý 3 bộ (luật chọn và chấm điểm, Gemini diễn giải). */
export default function ConceptPage() {
  const { stylist, context, catalog: CAT, loading } = useStore(); const { ask, open } = useActions();
  const tags = useContextTags(context); const [ms, setMs] = useState(0);
  useEffect(() => { setMs(stylist?.ms || 0); }, [stylist]);
  if (loading || !CAT) return <main className="page-container"><Stepper active={1} /><Loading /></main>;
  if (!stylist) return <main className="page-container"><EmptyState title="Cảm hứng bắt đầu từ bạn">Hãy cho stylist biết bối cảnh để có 3 bộ gợi ý dành riêng cho bạn.</EmptyState></main>;
  return <main className="page-container"><Stepper active={1} />
    <PageHeading eyebrow="3 GÓC NHÌN. MỘT CHẤT RIÊNG." title="Cảm hứng Việt, dành cho bạn." description="Chọn một bộ để bắt đầu. Bạn luôn có thể biến tấu theo cách mình thích." />
    {stylist.loading && <Loading text="Stylist đang chọn đồ…" />}
    {stylist.error && <ErrorBox message={stylist.error} retry={stylist.body ? () => ask(stylist.body!) : undefined} />}
    {stylist.res?.kind === 'clarify' && <section className="panel clarify"><p className="bubble">{stylist.res.question}</p>
      <div className="chips">{stylist.res.options.map(o => <button className="chip" key={o.label} onClick={() => ask({ ...stylist.body, override: { occasion: o.occasion || null } })}>{o.label}</button>)}</div></section>}
    {stylist.res?.kind === 'outfits' && <>
      <section className="understanding"><div><Sparkles size={21} /><strong>Stylist hiểu bạn đang tìm</strong></div><div className="tags">{tags.map(t => <span key={t}>{t}</span>)}</div>
        <p>Nguồn: <b>{stylist.res.source}</b>{ms ? ` · ${ms} ms` : ''}</p></section>
      <div className="concept-grid">{stylist.res.outfits.map((o, i) => <OutfitCard key={o.outfitId} o={o} index={i} onPick={() => open(o)} />)}</div></>}
    <Link to="/stylist" className="text-button back-link"><ArrowLeft size={17} /> Sửa bối cảnh</Link></main>;
}
