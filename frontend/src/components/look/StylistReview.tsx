import { MessageCircleHeart } from 'lucide-react';
import { ErrorBox, Loading } from '../common/UI';
import type { WardrobeReview } from '../../services/aiApi';
import { Recommend, ScoreCardView } from './ScoreCard';

/** Stylist nhận xét bộ đang mặc: tên bộ, lời nhận xét, Recommend và thẻ điểm 5 tiêu chí. */
export default function StylistReview({ review, busy, error, retry }: { review?: WardrobeReview | null; busy: boolean; error: string; retry: () => void }) {
  return <section className="review-section">
    <div>
      <span className="eyebrow"><MessageCircleHeart size={18}/> STYLIST NHẬN XÉT</span>
      <h2>Bộ đồ này hợp đến đâu?</h2>
      <p>Điểm do bộ luật chấm; Gemini chỉ diễn giải bằng lời.</p>
    </div>
    <div>
      {busy ? <Loading text="Stylist đang xem bộ đồ…"/> : error ? <ErrorBox message={error} retry={retry}/> : review && <>
        <div className={`verdict v-${review.verdict}`}>{review.verdictText}</div>
        <div className="bubble"><b>{review.current.title}</b><br/>{review.current.comment}
          <Recommend tip={review.current.tip} card={review.current.scoreCard}/></div>
        <div className="bubble"><ScoreCardView card={review.current.scoreCard}/></div>
        <p className="muted">Nguồn: <b>{review.source}</b></p></>}
    </div>
  </section>;
}
