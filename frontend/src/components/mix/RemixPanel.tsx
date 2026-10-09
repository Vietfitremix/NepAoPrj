import { ArrowRight, Compass } from 'lucide-react';
import type { WardrobeRemix } from '../../services/aiApi';

const STATUS: Record<WardrobeRemix['status'], { text: string; cls: string }> = {
  hop: { text: 'Yêu cầu hợp bối cảnh · đã áp dụng', cls: 'ok' },
  dieu_chinh: { text: 'Yêu cầu chưa hợp · đã áp dụng phương án gần ý nhất', cls: 'warn' },
  khong_hop: { text: 'Yêu cầu không hợp · giữ nguyên bộ hiện tại', cls: 'bad' },
  chua_ro: { text: 'Chưa rõ yêu cầu · giữ nguyên bộ hiện tại', cls: 'warn' },
};

/** Kết quả AI Remix: phân tích bối cảnh, nhận định thẳng thắn về yêu cầu, điểm trước/sau và các lựa chọn phù hợp hơn. */
export default function RemixPanel({ result, onPick, disabled }: { result: WardrobeRemix; onPick: (o: WardrobeRemix['options'][number]) => void; disabled?: boolean }) {
  const st = STATUS[result.status];
  return <section className="remix-result" role="status" aria-live="polite">
    <div className="remix-head"><Compass size={20}/><span className={`remix-status ${st.cls}`}>{st.text}</span>
      <span className="remix-scores">Điểm: {result.scoreBefore}{result.scoreRequested !== result.scoreBefore && <> → <b className={result.scoreRequested < result.scoreBefore - 5 ? 'low' : ''}>{result.scoreRequested}</b> (theo yêu cầu)</>}
        {result.scoreAfter !== result.scoreBefore || result.applied ? <> → <b>{result.scoreAfter}</b> (sau xử lý)</> : null}</span></div>
    <p className="remix-analysis"><b>Phân tích bối cảnh:</b> {result.analysis}</p>
    <p className="remix-explain">{result.explanation}</p>
    {result.options.length > 0 && <div className="remix-options"><span className="muted">Lựa chọn phù hợp hơn:</span>
      {result.options.map(o => <button key={o.label} type="button" className="remix-option" disabled={disabled} onClick={() => onPick(o)} title={o.why}>
        <span>{o.label}</span><small>{o.score}/100 · {o.band}</small><ArrowRight size={14}/></button>)}</div>}
  </section>;
}
