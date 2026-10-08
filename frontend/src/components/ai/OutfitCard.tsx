import { ArrowRight } from 'lucide-react';
import { useStore } from '../../ai/store';
import type { StylistOutfit } from '../../ai/types';
import { Figure } from './Figure';
import { Badges, ScoreMini } from './ScoreCardView';

export default function OutfitCard({ o, index, onPick, label = 'Chọn bộ này', onInfo }: { o: StylistOutfit; index?: number; onPick: () => void; label?: string; onInfo?: () => void }) {
  const { catalog: CAT } = useStore(); const s = o.state;
  if (!CAT) return null;
  const sub = [CAT.garment[s.garment]?.name, CAT.color[s.colors.main]?.name + (s.pattern && s.pattern !== 'tron' ? ' · ' + CAT.pattern[s.pattern]?.name : '')].join(' · ')
    + ` / ${CAT.color[s.colors.bottom]?.name}` + (s.accessories.length ? ' · ' + s.accessories.map(a => CAT.acc[a]?.name).join(', ') : '');
  return <article className="concept-card ocard">
    <div className={`concept-image concept-tone-${(index ?? 0) % 3}`}>
      {index !== undefined && <span className="concept-number">{String(index + 1).padStart(2, '0')} / 03</span>}
      <Figure state={s} className="ocard-fig" />
      {o.scoreCard && <span className="match-badge">✳ <ScoreMini card={o.scoreCard} /></span>}
    </div>
    <div className="concept-details">
      <span className="eyebrow">{CAT.occasion[s.occasion]?.name} · {CAT.style[s.style]?.name}</span>
      <h2>{o.title || CAT.garment[s.garment]?.name}</h2>
      <div className="muted">{sub}</div>
      {o.whyChosen && <div className="why">{o.whyChosen}</div>}
      <div className="badges"><Badges evals={o.evaluations} /></div>
      <p>{o.comment}</p>
      {o.tip && <div className="muted">Mẹo: {o.tip}</div>}
      {o.changes?.length ? <div className="muted">Thay đổi: {o.changes.join('; ')}</div> : null}
      {onInfo && <button className="text-button" onClick={onInfo}>Tìm hiểu câu chuyện trang phục</button>}
      <button className="button primary full-width" onClick={onPick}>{label} <ArrowRight size={17} /></button>
    </div>
  </article>;
}
