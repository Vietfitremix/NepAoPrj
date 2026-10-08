import type { Evaluation, ScoreCard } from '../../ai/types';
import { LEVEL } from '../../ai/actions';

export const ScoreMini = ({ card }: { card?: ScoreCard | null }) => card ? <span className="sc-mini"><b>{card.total}</b>/100 · {card.bandText}</span> : null;

export function ScoreCardView({ card }: { card?: ScoreCard | null }) {
  if (!card) return null;
  return <div className="sc">
    <div className="sc-head"><span className="sc-total">{card.total}</span><span className="muted">/100</span><span className={`sc-band ${card.band}`}>{card.bandText}</span>
      {card.capped && <span className="muted">(chặn trần vì có điểm dễ gây sai lệch)</span>}</div>
    {card.criteria.map(c => {
      const why = [...c.notes, ...c.ruleIds.map(id => 'luật ' + id)].join(' · ');
      return <div className="sc-row" key={c.id} title={c.en}>
        <span>{c.name} <span className="muted">{c.weight}%</span></span>
        <div className="sc-bar"><i className={c.score < 60 ? 'low' : ''} style={{ width: `${c.score}%` }} /></div><b>{c.score}</b>
        {why && <div className="sc-note muted">{why}</div>}
      </div>;
    })}
  </div>;
}
export function Badges({ evals }: { evals: Evaluation[] }) {
  if (!evals.length) return <span className="badge b-ok">Phù hợp</span>;
  return <>{evals.map((e, i) => <span key={i} className={`badge b-${e.level}`} title={e.reason}>{LEVEL[e.level]}</span>)}</>;
}

/** Lời khuyên của stylist: dùng mẹo Gemini viết; nếu chưa có thì gợi ý nâng tiêu chí thấp nhất của thẻ điểm. */
export function Recommend({ tip, card }: { tip?: string; card?: ScoreCard | null }) {
  const low = card ? [...card.criteria].sort((a, b) => a.score - b.score)[0] : null;
  const text = tip?.trim() || (low && low.score < 90 ? `Nâng tiêu chí “${low.name}” (đang ${low.score}/100) để bộ đồ chuẩn hơn.` : '');
  return text ? <p className="recommend"><b>Recommend:</b> {text}</p> : null;
}
