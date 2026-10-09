import { useState } from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import type { MixConfig, Outfit } from '../../types';
import { characterViews, rotateView } from '../../utils/characterViews';
import type { CharacterView } from '../../utils/characterViews';
import { outfitPreview } from '../../utils/outfitPreview';
import WardrobeFigure from './WardrobeFigure';
export default function Avatar2D({ outfit, config }: { outfit: Outfit; config: MixConfig }) {
  const [view, setView] = useState<CharacterView>('front');
  const character = config.wardrobe?.character ?? 'female';
  const selection = outfitPreview(config, character);
  return <section className="figwrap panel" aria-label="Xem bản phối bốn góc">
    <div className="bigfig"><WardrobeFigure selection={selection} character={character} view={view} label={`Bản phối ${outfit.name}, góc ${characterViews.find(item => item.id === view)?.label}`}/></div>
    <div className="viewnav">
      <button type="button" className="icon-button" aria-label="Góc trước đó" onClick={() => setView(rotateView(view, -1))}><ChevronLeft size={18}/></button>
      <span className="muted">{characterViews.find(item => item.id === view)?.label}</span>
      <button type="button" className="icon-button" aria-label="Góc kế tiếp" onClick={() => setView(rotateView(view, 1))}><ChevronRight size={18}/></button>
    </div>
    <div className="views">{characterViews.map(item => <button type="button" key={item.id} aria-pressed={item.id === view} onClick={() => setView(item.id)}>
      <WardrobeFigure selection={selection} character={character} view={item.id} label={`${outfit.name}, góc ${item.label}`} className="view-thumb"/><span>{item.label}</span>
    </button>)}</div>
  </section>;
}
