import { useEffect, useRef, useState } from 'react';
import { BookOpen, X, ArrowUpRight } from 'lucide-react';
import { getCulturalKnowledge } from '../../services/culturalApi';
import { errorMessage } from '../../services/api';
import type { CulturalKnowledge, CulturalSection } from '../../types';
import { ErrorBox, Loading } from '../common/UI';
export function CulturalContent({ knowledge }: { knowledge: CulturalKnowledge }) {
  const sections: CulturalSection[] = knowledge.sections?.length ? knowledge.sections : [
    { category: 'ORIGIN', title: 'Nguồn gốc', paragraphs: [knowledge.origin] },
    { category: 'MEANING', title: 'Ý nghĩa văn hóa', paragraphs: [knowledge.meaning] },
    { category: 'CHARACTERISTICS', title: 'Đặc trưng', paragraphs: [knowledge.characteristics] }
  ];
  const sources = [...new Map([
    ...(knowledge.sources || []), ...sections.flatMap(section => section.source ? [section.source] : [])
  ].filter(source => /^https?:\/\//i.test(source.url)).map(source => [source.url, source])).values()];
  return <div className="cultural-content">
    {sections.map((section, index) => <section key={`${section.category}-${index}`} data-culture-category={section.category}>
      <h3>{section.title}</h3>
      {section.paragraphs.map((paragraph, paragraphIndex) => <p key={paragraphIndex}>{paragraph}</p>)}
      {section.source && /^https?:\/\//i.test(section.source.url) && <a className="culture-section-source"
        href={section.source.url} target="_blank" rel="noreferrer" title={section.source.title}
        aria-label={`Nguồn cho ${section.title}: ${section.source.title}`}>
        Nguồn [{sources.findIndex(source => source.url === section.source!.url) + 1}] <ArrowUpRight size={12}/>
      </a>}
    </section>)}
    {sources.length ? <section className="culture-bibliography"><h3>Nguồn tham khảo</h3>
      {sources.map((source, index) => <a className="source-link" key={source.url} href={source.url} target="_blank" rel="noreferrer">
        <span>[{index + 1}] {source.title}</span><ArrowUpRight size={14}/>
      </a>)}
    </section> : <p className="muted">Backend chưa cung cấp liên kết nguồn tham khảo.</p>}
  </div>;
}
export default function CulturalInfoModal({ code, onClose, onSelect }: { code: string; onClose: ()=>void; onSelect: ()=>void }) {
  const dialog = useRef<HTMLDialogElement>(null); const [data,setData]=useState<CulturalKnowledge>();const [error,setError]=useState('');const [retry,setRetry]=useState(0);
  useEffect(()=>{const element=dialog.current; const previous=document.activeElement as HTMLElement; element?.showModal();const overflow=document.body.style.overflow;document.body.style.overflow='hidden';return()=>{element?.close();document.body.style.overflow=overflow;previous?.focus();};},[]);
  useEffect(()=>{const controller=new AbortController();setData(undefined);setError('');getCulturalKnowledge(code,controller.signal).then(result=>{if(!controller.signal.aborted)setData(result);}).catch(err=>{if(!controller.signal.aborted)setError(errorMessage(err));});return()=>controller.abort();},[code,retry]);
  return <dialog ref={dialog} className="culture-modal" aria-labelledby="culture-title" onCancel={onClose} onClick={e=>{if(e.target===dialog.current)onClose();}}><div className="modal-inner"><button className="icon-button modal-close" onClick={onClose} aria-label="Đóng thông tin văn hóa"><X/></button><span className="eyebrow"><BookOpen size={17}/> CÂU CHUYỆN VIỆT PHỤC</span><h2 id="culture-title">{data?.name||'Tìm hiểu trang phục'}</h2>{error?<ErrorBox message={error} retry={()=>setRetry(v=>v+1)}/>:data?<CulturalContent knowledge={data}/>:<Loading/>}<button className="button primary full-width" onClick={onSelect}>Chọn trang phục này</button></div></dialog>;
}
