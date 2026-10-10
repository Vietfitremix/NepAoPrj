import { ArrowRight, BookOpen } from 'lucide-react';
import type { Concept } from '../../types';
import WardrobeFigure from '../mix/WardrobeFigure';
import { outfitPreview } from '../../utils/outfitPreview';
import type { WardrobeCharacter } from '../../utils/maleWardrobe';

export default function ConceptCard({ concept, index, onInfo, onSelect, character = 'female' }: {
  concept: Concept; index: number; onInfo: () => void; onSelect: () => void; character?: WardrobeCharacter;
}) {
  return <article className="concept-card ocard">
    <div className={`concept-image concept-tone-${index}`}>
      <span className="concept-number">{String(index + 1).padStart(2, '0')} / 03</span>
      <WardrobeFigure character={character} selection={outfitPreview({ ...concept, accessoryCodes:concept.accessoryCodes ?? [] }, character)} label={concept.name} className="ocard-fig"/>
      <span className="match-badge"><img className="badge-lotus-icon" src="/lotus-logo-transparent.png" alt="" aria-hidden="true"/><span><b>{concept.matchScore}</b>/100 · Phù hợp</span></span>
    </div>
    <div className="concept-details"><span className="eyebrow">{concept.outfitName} · {concept.styleName}</span>
      <h2>{concept.name}</h2><div className="muted">{concept.colorName} · {concept.styleName}</div>
      <div className="why">{concept.reason}</div>
      <button className="text-button" onClick={onInfo}><BookOpen size={16}/> Tìm hiểu câu chuyện trang phục</button>
      <button className="button primary full-width" onClick={onSelect}>Chọn bộ này <ArrowRight size={17}/></button>
    </div>
  </article>;
}
