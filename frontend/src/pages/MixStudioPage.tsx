import { useEffect, useMemo, useRef, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ArrowLeft, ArrowRight, Share2 } from 'lucide-react';
import { EmptyState, Loading, PageHeading, Stepper } from '../components/common/UI';
import { Figure, useFigure } from '../components/ai/Figure';
import { Badges, ScoreCardView } from '../components/ai/ScoreCardView';
import ShareDialog from '../components/ai/ShareDialog';
import { LEVEL, fullContext, reviewKey } from '../ai/actions';
import { aiApi } from '../ai/api';
import { motifTop, patternDef, patternOk, SLOT_NAME, SLOT_ORDER, VIEWS } from '../ai/figure';
import { useStore } from '../ai/store';
import type { EvaluateResponse, OutfitState } from '../ai/types';
import { useContextTags } from './ConceptPage';

const SWATCH_SLOTS: [keyof OutfitState['colors'], string][] = [['main', 'Màu chính'], ['bottom', 'Quần / váy'], ['lining', 'Lót / viền / yếm'], ['accent', 'Khăn / thắt lưng / điểm nhấn']];

/** Bước 3: tuỳ chỉnh bộ đồ. Người mẫu giấy 4 góc, màu theo từng vị trí, hoạ tiết, phụ kiện; thẻ điểm và cảnh báo văn hoá chấm lại theo luật mỗi lần đổi. */
export default function MixStudioPage() {
  const store = useStore(); const { state, context, view, catalog: CAT, review, set, loading } = store; const navigate = useNavigate();
  const [ev, setEv] = useState<EvaluateResponse | null>(null); const [evErr, setEvErr] = useState('');
  const [share, setShare] = useState(false);
  const tags = useContextTags(state ? fullContext(context, state) : null);
  const big = useFigure(state, view);
  const timer = useRef<number | undefined>(undefined);
  const ctxKey = state ? JSON.stringify(fullContext(context, state)) : '';

  useEffect(() => {
    if (!state) return;
    window.clearTimeout(timer.current);
    timer.current = window.setTimeout(async () => {
      try { setEv(await aiApi<EvaluateResponse>('/evaluate', { state, context: fullContext(context, state) })); setEvErr(''); }
      catch (e) { setEvErr(e instanceof Error ? e.message : String(e)); }
    }, 150);
    return () => window.clearTimeout(timer.current);
    // eslint-disable-next-line
  }, [JSON.stringify(state), ctxKey]);

  const patterns = useMemo(() => CAT && state ? CAT.patterns.filter(p => patternOk(p, state)) : [], [CAT, state]);
  if (loading || !CAT) return <main className="page-container"><Stepper active={2} /><Loading /></main>;
  if (!state) return <main className="page-container"><EmptyState title="Chưa có bộ nào để tuỳ chỉnh">Hãy chọn một trong 3 bộ stylist gợi ý.</EmptyState></main>;

  const update = (patch: Partial<OutfitState>) => set({ state: { ...state, ...patch }, review: { key: null, res: null } });
  const setGender = (gender: string) => {
    const ok = CAT.garments.filter(g => g.genders.includes(gender));
    const garment = ok.some(g => g.id === state.garment) ? state.garment : ok[0].id;
    update({ gender, garment, accessories: state.accessories.filter(a => CAT.acc[a].genders.includes(gender)), pattern: patternOk(CAT.pattern[state.pattern || 'tron'] || {}, { ...state, gender, garment }) ? state.pattern : 'tron' });
  };
  const setGarment = (garment: string) => update({ garment, pattern: patternOk(CAT.pattern[state.pattern || 'tron'] || {}, { ...state, garment }) ? state.pattern : 'tron' });
  const toggleAcc = (id: string, on: boolean) => {
    const slot = CAT.acc[id].slot;
    const rest = state.accessories.filter(x => CAT.acc[x].slot !== slot);
    update({ accessories: on ? [...rest, id] : rest });
  };
  const applyPatch = (p: Record<string, unknown>) => {
    const next = { ...state } as Record<string, unknown>;
    for (const [k, v] of Object.entries(p)) next[k] = k === 'colors' ? { ...state.colors, ...(v as object) } : v;
    set({ state: next as unknown as OutfitState, review: { key: null, res: null } });
  };
  const base = CAT.color[state.colors.main]?.hex || '#ccc';
  const accOk = CAT.accessories.filter(a => a.genders.includes(state.gender));
  const card = CAT.cultureCards.find(c => c.garmentId === state.garment);
  const fresh = review.key === reviewKey(context, state);
  const vi = VIEWS.findIndex(x => x[0] === view);

  return <main className="page-container wide"><Stepper active={2} />
    <PageHeading eyebrow="YOUR STYLE. YOUR STORY." title="Một chút remix. Một chất riêng." description="Thử màu mới, đổi hoạ tiết, thêm phụ kiện. Thẻ điểm bên cạnh chấm lại ngay theo bối cảnh của bạn." />
    <div className="tags ctx"><span className="muted">Bối cảnh:</span>{tags.map(t => <span key={t}>{t}</span>)}</div>
    <div className="studio">
      <div className="figwrap panel">
        <div className="bigfig"><Figure state={state} view={view} /></div>
        <div className="viewnav"><button className="icon-button" aria-label="Góc trước đó" onClick={() => set({ view: VIEWS[(vi + 3) % 4][0] })}>◀</button><span className="muted">{VIEWS[vi][1]}</span>
          <button className="icon-button" aria-label="Góc kế tiếp" onClick={() => set({ view: VIEWS[(vi + 1) % 4][0] })}>▶</button></div>
        <div className="views">{VIEWS.map(([v, name]) => <ViewThumb key={v} state={state} v={v} name={name} active={v === view} onPick={() => set({ view: v })} />)}</div>
        {big?.missing.length ? <div className="missing">Chưa có hình: {big.missing.join(', ')}</div> : null}
      </div>
      <div className="controls panel">
        <div className="selects">
          <Field label="Người mẫu"><select value={state.gender} onChange={e => setGender(e.target.value)}><option value="nu">Nữ</option><option value="nam">Nam</option></select></Field>
          <Field label="Dịp"><select value={state.occasion} onChange={e => update({ occasion: e.target.value })}>{CAT.occasions.map(o => <option key={o.id} value={o.id}>{o.name}</option>)}</select></Field>
          <Field label="Phong cách"><select value={state.style} onChange={e => update({ style: e.target.value })}>{CAT.styles.map(o => <option key={o.id} value={o.id}>{o.name}</option>)}</select></Field>
          <Field label="Trang phục"><select value={state.garment} onChange={e => setGarment(e.target.value)}>{CAT.garments.filter(g => g.genders.includes(state.gender)).map(g => <option key={g.id} value={g.id}>{g.name}{g.hasSvg === false ? ' (chưa có hình)' : ''}</option>)}</select></Field>
        </div>
        {SWATCH_SLOTS.map(([slot, label]) => <Field key={slot} label={label}><div className="swatches">{CAT.colors.map(c =>
          <button key={c.id} className="sw" title={c.name} style={{ background: c.hex }} aria-pressed={state.colors[slot] === c.id}
            onClick={() => update({ colors: { ...state.colors, [slot]: c.id } })} />)}</div></Field>)}
        <Field label="Hoạ tiết"><div className="accs">{[...new Set(patterns.map(p => p.group || ''))].map(gr => <div className="accgroup" key={gr}>{gr && <span className="muted">{gr}</span>}
          {patterns.filter(p => (p.group || '') === gr).map((p, i) => {
            const def = patternDef(p.id, base, `sw_pat_${gr}_${i}`);
            const art = p.kind === 'placement' ? `<rect width="44" height="44" fill="${base}"/><g transform="translate(2 -2) scale(0.4)">${motifTop(p.id)}</g>`
              : `${def ? `<defs>${def}</defs>` : ''}<rect width="44" height="44" fill="${def ? `url(#sw_pat_${gr}_${i})` : base}"/>`;
            return <button key={p.id} className="pat" title={p.name + (p.note ? ' – ' + p.note : '')} aria-pressed={(state.pattern || 'tron') === p.id} onClick={() => update({ pattern: p.id })}>
              <svg viewBox="0 0 44 44" dangerouslySetInnerHTML={{ __html: art }} /></button>;
          })}</div>)}</div></Field>
        <Field label="Phụ kiện (mỗi vị trí 1 món)"><div className="accs">{[...SLOT_ORDER].reverse().filter(sl => accOk.some(a => a.slot === sl)).map(sl => <div className="accgroup" key={sl}><span className="muted">{SLOT_NAME[sl]}</span>
          {accOk.filter(a => a.slot === sl).map(a => <label key={a.id}><input type="checkbox" checked={state.accessories.includes(a.id)} onChange={e => toggleAcc(a.id, e.target.checked)} /> {a.name}</label>)}</div>)}</div></Field>
      </div>
      <aside className="cultural-panel panel" aria-live="polite">
        <div className="small-panel-heading"><h2>Thẻ điểm và kiểm tra văn hoá</h2></div>
        {ev ? <><ScoreCardView card={ev.scoreCard} /><p className="muted">Màu: {ev.color.note}</p>
          {ev.evaluations.length ? ev.evaluations.map((e, i) => <div className={`eval ${e.level}`} key={i}><span className={`badge b-${e.level}`}>{LEVEL[e.level]}</span> {e.reason}
            <div className="muted">Gợi ý: {e.suggestion.text} {e.suggestion.patch && <button className="chip" onClick={() => applyPatch(e.suggestion.patch!)}>Áp dụng</button>}</div></div>)
            : <div className="eval ok"><span className="badge b-ok">Phù hợp</span> Không có cảnh báo văn hoá nào cho bộ này.</div>}</>
          : evErr ? <p className="warn">{evErr}</p> : <Loading text="Đang chấm điểm…" />}
        {card && <div className="culture"><b>{card.title}</b> {!card.verified && <span className="muted">(chưa kiểm chứng nguồn)</span>}<br />{card.body}</div>}
      </aside>
    </div>
    <div className="pagebar">
      <Link className="text-button" to="/concepts"><ArrowLeft size={16} /> Chọn bộ khác</Link>
      <div className="row">{fresh && <span className="muted">Bộ đồ chưa đổi kể từ lần hỏi trước, sẽ xem lại nhận xét cũ.</span>}
        <button className="button outline" onClick={() => setShare(true)}><Share2 size={16} /> Checklist &amp; Lookbook</button>
        <button className="button primary" onClick={() => navigate('/look')}>Hỏi stylist <ArrowRight size={16} /></button></div>
    </div>
    <ShareDialog open={share} onClose={() => setShare(false)} state={state} note={{ title: '', comment: '', tip: '', card: ev?.scoreCard }} />
  </main>;
}

function Field({ label, children }: { label: string; children: React.ReactNode }) { return <div className="field"><span className="t">{label}</span>{children}</div>; }
function ViewThumb({ state, v, name, active, onPick }: { state: OutfitState; v: string; name: string; active: boolean; onPick: () => void }) {
  const r = useFigure(state, v);
  return <button aria-pressed={active} onClick={onPick}><span className="thumb" dangerouslySetInnerHTML={{ __html: r?.svg || '' }} /><span>{name}</span></button>;
}
export { Badges };
