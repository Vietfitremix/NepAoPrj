import { useEffect, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { ArrowLeft, Share2 } from 'lucide-react';
import { EmptyState, ErrorBox, Loading, PageHeading, Stepper } from '../components/common/UI';
import { Figure } from '../components/ai/Figure';
import OutfitCard from '../components/ai/OutfitCard';
import { ScoreCardView } from '../components/ai/ScoreCardView';
import ShareDialog from '../components/ai/ShareDialog';
import { fullContext, reviewKey, useActions } from '../ai/actions';
import { aiApi, loadLook, saveLook } from '../ai/api';
import { VIEWS } from '../ai/figure';
import { useStore } from '../ai/store';
import type { ReviewResponse, SavedLook } from '../ai/types';
import { useContextTags } from './ConceptPage';

/** Bước 4: stylist nhận xét bộ đang mặc (kèm thẻ điểm và phương án nâng cấp); lưu look để chia sẻ bằng liên kết. */
export default function FinalLookPage() {
  const { state, context, review, set, reset, catalog: CAT, loading } = useStore(); const { open } = useActions(); const navigate = useNavigate();
  const [err, setErr] = useState(''); const [busy, setBusy] = useState(false); const [share, setShare] = useState(false);
  const [link, setLink] = useState(''); const [saving, setSaving] = useState(false);
  const tags = useContextTags(state ? fullContext(context, state) : null);
  const key = state ? reviewKey(context, state) : '';

  useEffect(() => {
    if (!state || !CAT || review.key === key) return;
    let live = true; setBusy(true); setErr('');
    aiApi<ReviewResponse>('/review', { state, context: fullContext(context, state) })
      .then(res => { if (live) set({ review: { key, res } }); })
      .catch(e => { if (live) setErr(e instanceof Error ? e.message : String(e)); })
      .finally(() => { if (live) setBusy(false); });
    return () => { live = false; };
    // eslint-disable-next-line
  }, [key, !!CAT]);

  if (loading || !CAT) return <main className="page-container"><Stepper active={3} /><Loading /></main>;
  if (!state) return <main className="page-container"><EmptyState title="Chưa có bộ nào để nhận xét">Hãy chọn một bộ stylist gợi ý rồi tuỳ chỉnh.</EmptyState></main>;
  const r = review.key === key ? review.res : null;
  const note = { title: r?.current.title || '', comment: r?.current.comment || '', tip: r?.current.tip || '', card: r?.current.scoreCard };

  async function save() {
    setSaving(true); setErr('');
    try {
      const id = await saveLook({ state, context: fullContext(context, state!), scoreCard: note.card ?? null, note: { title: note.title, comment: note.comment, tip: note.tip } });
      setLink(`${window.location.origin}/look/${id}`);
    } catch (e) { setErr(e instanceof Error ? e.message : String(e)); } finally { setSaving(false); }
  }
  return <main className="page-container wide"><Stepper active={3} />
    <PageHeading eyebrow="YOUR VIỆT LOOK" title="Stylist nhận xét bộ của bạn." description="Nhận xét dựa trên luật chấm của hệ thống; Gemini chỉ diễn giải bằng lời." />
    <div className="review">
      <div><div className="fig4">{VIEWS.map(([v, name]) => <div key={v}><Figure state={state} view={v} /><span className="muted">{name}</span></div>)}</div>
        <div className="tags ctx"><span className="muted">Bối cảnh:</span>{tags.map(t => <span key={t}>{t}</span>)}</div></div>
      <div>
        {busy && <Loading text="Stylist đang xem bộ đồ…" />}
        {err && <ErrorBox message={err} />}
        {r && <>
          <div className={`verdict v-${r.verdict}`}>{r.verdictText}</div><p className="muted">Nguồn: <b>{r.source}</b></p>
          <div className="bubble"><b>{r.current.title}</b><br />{r.current.comment}<div className="muted">Mẹo: {r.current.tip}</div></div>
          <div className="bubble"><ScoreCardView card={r.current.scoreCard} /></div>
          {r.alternatives.length ? <><h3 className="alt-title">Phương án nâng cấp</h3><div className="alt-grid">{r.alternatives.map(a => <OutfitCard key={a.outfitId} o={a} label="Áp dụng phương án này" onPick={() => open(a)} />)}</div></>
            : <p className="muted">Bộ này đã ổn, chưa có phương án nâng cấp rõ rệt.</p>}</>}
      </div>
    </div>
    {link && <div className="share-notice">Liên kết look của bạn (lưu trên máy chủ, ai có link đều xem được): <input readOnly value={link} onFocus={e => e.currentTarget.select()} /></div>}
    <div className="pagebar">
      <Link className="text-button" to="/mix"><ArrowLeft size={16} /> Tiếp tục chỉnh</Link>
      <div className="row">
        <button className="button outline" onClick={() => setShare(true)}><Share2 size={16} /> Checklist &amp; Lookbook</button>
        <button className="button outline" disabled={saving} onClick={save}>{saving ? 'Đang lưu…' : 'Lưu look & lấy liên kết'}</button>
        <button className="button primary" onClick={() => { reset(); navigate('/stylist'); }}>Bắt đầu lại</button></div>
    </div>
    <ShareDialog open={share} onClose={() => setShare(false)} state={state} note={note} />
  </main>;
}

/** Xem look đã lưu: /look/:id */
export function SharedLookPage() {
  const { id = '' } = useParams(); const { catalog: CAT, loading, set } = useStore(); const navigate = useNavigate();
  const [look, setLook] = useState<SavedLook>(); const [err, setErr] = useState(''); const [share, setShare] = useState(false);
  useEffect(() => { loadLook<SavedLook>(id).then(setLook).catch(e => setErr(e instanceof Error ? e.message : String(e))); }, [id]);
  if (err) return <main className="page-container"><ErrorBox message={err} /></main>;
  if (!look || loading || !CAT) return <main className="page-container"><Loading /></main>;
  const s = look.state, note = { title: look.note?.title || '', comment: look.note?.comment || '', tip: look.note?.tip || '', card: look.scoreCard };
  return <main className="page-container wide"><PageHeading eyebrow="YOUR VIỆT LOOK" title={note.title || CAT.garment[s.garment]?.name || 'Việt look'} description="Một bản phối được chia sẻ từ Nếp Áo." />
    <div className="review"><div className="fig4">{VIEWS.map(([v, name]) => <div key={v}><Figure state={s} view={v} /><span className="muted">{name}</span></div>)}</div>
      <div>{note.comment && <div className="bubble">{note.comment}<div className="muted">Mẹo: {note.tip}</div></div>}<div className="bubble"><ScoreCardView card={look.scoreCard} /></div></div></div>
    <div className="pagebar"><span />
      <div className="row"><button className="button outline" onClick={() => setShare(true)}><Share2 size={16} /> Checklist &amp; Lookbook</button>
        <button className="button primary" onClick={() => { set({ state: s, context: look.context ?? null, view: 'truoc', review: { key: null, res: null } }); navigate('/mix'); }}>Remix bộ này</button></div></div>
    <ShareDialog open={share} onClose={() => setShare(false)} state={s} note={note} />
  </main>;
}
