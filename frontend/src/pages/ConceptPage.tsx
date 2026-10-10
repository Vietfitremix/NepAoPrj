import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ArrowLeft, Sparkles } from 'lucide-react';
import { useSession } from '../state';
import { EmptyState, PageHeading, Stepper } from '../components/common/UI';
import ConceptCard from '../components/concept/ConceptCard';
import CulturalInfoModal from '../components/concept/CulturalInfoModal';
import type { Concept } from '../types';
import { cities } from './StylistPage';
import { initialWardrobe } from '../utils/mixWardrobe';
import type { MixConfig } from '../types';
export default function ConceptPage() {
  const { session, update }=useSession();const navigate=useNavigate();const [info,setInfo]=useState<Concept>();const { recommendation, preferences }=session;
  function select(concept: Concept){const mix:MixConfig={conceptId:concept.id,outfitCode:concept.outfitCode,colorCode:concept.colorCode,styleCode:concept.styleCode,eventCode:preferences?.eventCode||'TET',accessoryCodes:concept.accessoryCodes||[]};mix.wardrobe=initialWardrobe(mix,preferences?.character||'female');update({mix});navigate(`/mix/${encodeURIComponent(concept.id)}`);}
  if(!recommendation||!preferences)return <main className="page-container nepao-page"><EmptyState title="Cảm hứng bắt đầu từ bạn">Hãy chia sẻ sở thích để AI tạo 3 concept dành riêng cho bạn.</EmptyState></main>;
  const weather = recommendation.weather || preferences.weather;
  return <main className="page-container nepao-page">
    <Stepper active={1}/>
    <PageHeading eyebrow="3 GÓC NHÌN – MỘT CHẤT RIÊNG" title="Cảm hứng Việt, dành cho bạn."
      description="Chọn một concept để bắt đầu. Bạn luôn có thể biến tấu theo cách mình thích."/>
    <section className="understanding">
      <div><Sparkles size={21}/><strong>AI hiểu bạn đang tìm</strong></div>
      <p>{recommendation.understanding}</p>
      <div className="tags"><span>Thời tiết hiện tại tại {cities.find(c => c.code === weather.city)?.label || weather.city || preferences.city}: {Math.round(weather.temperature)}°C</span></div>
    </section>
    <div className="concept-grid">{recommendation.concepts.map((concept, i) =>
      <ConceptCard key={concept.id} concept={concept} index={i} character={preferences.character || 'female'}
        onInfo={() => setInfo(concept)} onSelect={() => select(concept)}/>)}</div>
    <Link to="/stylist" className="text-button back-link"><ArrowLeft size={17}/> Điều chỉnh nhu cầu của bạn</Link>
    {info && <CulturalInfoModal code={info.outfitCode} onClose={() => setInfo(undefined)} onSelect={() => select(info)}/>}
  </main>;
}
