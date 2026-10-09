import type { CulturalResult } from '../../types';
import { contextLabels } from '../../utils/outfitContext';

export default function AssessmentDetails({ result }: { result: CulturalResult }) {
  const assessment = result.assessment;
  if (!assessment) return null;
  const labels = (keys: string[]) => keys.map(key => contextLabels[key] || key).join(', ');
  return <details className="assessment-details">
    <summary>Chi tiết kiểm tra · {assessment.matchedRuleCount}/{assessment.ruleCount} luật khớp</summary>
    {Object.keys(assessment.contextUsed).length > 0 && <p>Bối cảnh đã dùng: {labels(Object.values(assessment.contextUsed))}.</p>}
    {assessment.missingContext.length > 0 && <p className="muted">Chưa có {labels(assessment.missingContext)}. Các luật cần thông tin này chưa áp dụng.</p>}
    <p className="muted">Tác động dưới đây là điểm cơ bản của từng tiêu chí, trước trọng số và điều chỉnh theo phong cách. Các luật cùng vấn đề chỉ tính một lần.</p>
    <ul>{result.checks?.map(check => <li key={check.ruleId}>
      <strong>{check.title}</strong><span className={check.points > 0 ? 'assessment-positive' : 'assessment-consider'}> {check.points > 0 ? '+' : ''}{check.points}</span>
      <p>{check.reason}</p><p className="muted">Gợi ý: {check.suggestion}</p>
    </li>)}</ul>
  </details>;
}
