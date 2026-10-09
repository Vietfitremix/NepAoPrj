import WardrobeFigure from '../mix/WardrobeFigure';
export default function OutfitArt({ color = '#923930', variant = 'long', className = '' }: {
  color?: string; variant?: 'long' | 'royal' | 'casual'; className?: string;
}) {
  const shirt = variant === 'royal' ? 'nhat-binh' : variant === 'casual' ? 'ba-ba' : 'jade';
  return <WardrobeFigure className={`outfit-art ${className}`} label="Minh họa phối trang phục Việt"
    selection={{ shirt, pants:'ivory', shoes:'hai-theu', styles:{shirt:{color}} }}/>
}
