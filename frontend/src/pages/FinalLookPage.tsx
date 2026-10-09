import { useEffect, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { ArrowLeft, BookOpen, Check, Heart, Share2, Sparkles } from 'lucide-react';
import type { CulturalKnowledge, Look } from '../types';
import { getLook } from '../services/lookApi';
import WardrobeFigure from '../components/mix/WardrobeFigure';
import { outfitPreview } from '../utils/outfitPreview';
import { characterViews } from '../utils/characterViews';
import { getCulturalKnowledge } from '../services/culturalApi';
import { errorMessage } from '../services/api';
import { useSession } from '../state';
import StylistReview from '../components/look/StylistReview';
import ShareDialog from '../components/look/ShareDialog';
import { lookbookExtras, noteOf, wardrobeReview } from '../services/aiApi';
import type { WardrobeReview } from '../services/aiApi';
import { downloadCanvas, drawLookbook } from '../utils/lookbook';
import type { LookbookExtras } from '../utils/lookbook';
import { normalizeMaleSelection } from '../utils/maleWardrobe';
import { ErrorBox, Loading, PageHeading, Stepper } from '../components/common/UI';
import { CulturalContent } from '../components/concept/CulturalInfoModal';
function savedIds(): string[] {
  try {
    const value: unknown = JSON.parse(localStorage.getItem('viet-fit-saved-looks') || '[]');
    return Array.isArray(value) ? value.filter((id): id is string => typeof id === 'string') : [];
  } catch { return []; }
}
export default function FinalLookPage(){
  const {lookId}=useParams();const navigate=useNavigate();const {session,update}=useSession();const [look,setLook]=useState<Look>();const [knowledge,setKnowledge]=useState<CulturalKnowledge>();const [error,setError]=useState('');const [cultureError,setCultureError]=useState('');const [retry,setRetry]=useState(0);const [cultureRetry,setCultureRetry]=useState(0);const [saved,setSaved]=useState(false);const [notice,setNotice]=useState('');const [sharing,setSharing]=useState(false);const [review,setReview]=useState<WardrobeReview|null>(null);const [reviewBusy,setReviewBusy]=useState(false);const [reviewError,setReviewError]=useState('');const [reviewRetry,setReviewRetry]=useState(0);const [extras,setExtras]=useState<Pick<LookbookExtras,'tips'|'cultureCards'>>({tips:{},cultureCards:[]});const [dialog,setDialog]=useState(false);const [tab,setTab]=useState<'card'|'views'>('card');const [card,setCard]=useState<HTMLCanvasElement|null>(null);const [cardUrl,setCardUrl]=useState('');const [cardError,setCardError]=useState('');
  useEffect(()=>{if(!lookId)return;const controller=new AbortController();setLook(undefined);setError('');setNotice('');setSaved(savedIds().includes(lookId));getLook(lookId,controller.signal).then(data=>{if(!controller.signal.aborted)setLook(data);}).catch(err=>{if(!controller.signal.aborted)setError(errorMessage(err));});return()=>controller.abort();},[lookId,retry]);
  useEffect(()=>{if(!look)return;setKnowledge(undefined);setCultureError('');const controller=new AbortController();getCulturalKnowledge(look.outfitCode,controller.signal).then(data=>{if(!controller.signal.aborted)setKnowledge(data);}).catch(err=>{if(!controller.signal.aborted)setCultureError(errorMessage(err));});return()=>controller.abort();},[look,cultureRetry]);
  useEffect(()=>{if(!look?.config.wardrobe)return;const controller=new AbortController();setReview(null);setReviewError('');setReviewBusy(true);
    wardrobeReview(look.config,session.preferences?.answers,controller.signal).then(data=>{if(!controller.signal.aborted)setReview(data);})
      .catch(err=>{if(!controller.signal.aborted)setReviewError(errorMessage(err));}).finally(()=>{if(!controller.signal.aborted)setReviewBusy(false);});
    return()=>controller.abort();// eslint-disable-next-line react-hooks/exhaustive-deps
  },[look?.id,reviewRetry]);
  useEffect(()=>{const controller=new AbortController();lookbookExtras(controller.signal).then(data=>{if(!controller.signal.aborted)setExtras(data);}).catch(()=>{/* checklist vẫn dùng được, chỉ thiếu mẹo */});return()=>controller.abort();},[]);
  useEffect(()=>{const w=look?.config.wardrobe;if(!w||reviewBusy)return;let live=true;setCardError('');
    drawLookbook(normalizeMaleSelection(w.selection,w.character),w.character,noteOf(review),{...extras,styleName:look!.styleName,eventName:look!.eventName})
      .then(c=>{if(live){setCard(c);setCardUrl(c.toDataURL('image/png'));}}).catch(()=>{if(live)setCardError('Chưa vẽ được thẻ Lookbook. Hãy thử lại sau.');});
    return()=>{live=false;};// eslint-disable-next-line react-hooks/exhaustive-deps
  },[look?.id,review,reviewBusy,extras]);
  const styleMatch=(()=>{const card=review?.current.scoreCard;if(!card)return null;const v=(id:string)=>card.criteria.find(c=>c.id===id)?.score??0;
    const avg=Math.round((v('boi_canh')+v('cach_tan')+v('cau_truc'))/3);return card.capped?Math.min(avg,card.total+10):avg;})();
  const harmony=review?.current.color?.score??null;
  function save(){if(!look)return;try{const ids=savedIds();localStorage.setItem('viet-fit-saved-looks',JSON.stringify(saved?ids.filter(id=>id!==look.id):[...new Set([...ids,look.id])]));setSaved(!saved);setNotice(saved?'Đã bỏ lưu look trên thiết bị này.':'Đã lưu look trên thiết bị này.');}catch{setNotice('Trình duyệt không cho phép lưu. Bạn có thể sao chép liên kết look.');}}
  async function share(){if(!look)return;setSharing(true);try{if(navigator.share)await navigator.share({title:`${look.name} — VIỆT FIT`,text:'Mặc chất riêng. Giữ hồn Việt.',url:window.location.href});else{await navigator.clipboard.writeText(window.location.href);setNotice('Đã sao chép liên kết look.');}}catch(err){if(!(err instanceof DOMException&&err.name==='AbortError'))setNotice('Chưa thể chia sẻ tự động. Hãy sao chép liên kết bên dưới.');}finally{setSharing(false);}}
  return <main className="page-container nepao-page wide"><Stepper active={3}/><PageHeading eyebrow="YOUR VIỆT LOOK" title="Rất Việt Nam. Rất là bạn." description="Một bản phối mang dấu ấn riêng, một câu chuyện để tự hào chia sẻ."/>{error?<ErrorBox message={error} retry={()=>setRetry(v=>v+1)}/>:!look?<Loading text="Đang mở Việt look của bạn…"/>:<><div className="final-layout"><div className={`final-art ${tab==='card'?'is-card':''}`}>
<div className="art-tabs" role="tablist"><button type="button" role="tab" aria-selected={tab==='card'} className={tab==='card'?'on':''} onClick={()=>setTab('card')}>Thẻ Lookbook</button>
<button type="button" role="tab" aria-selected={tab==='views'} className={tab==='views'?'on':''} onClick={()=>setTab('views')}>4 góc nhìn</button></div>
{tab==='card'?<div className="lookbook-card">{cardUrl?<img src={cardUrl} alt="Thẻ Lookbook của bản phối"/>:cardError?<p className="muted">{cardError}</p>:<Loading text="Đang vẽ thẻ Lookbook…"/>}
{card&&<button type="button" className="button outline" onClick={()=>downloadCanvas(card,`nep-ao-lookbook-${look.id}.png`)}>Tải thẻ Lookbook (PNG)</button>}</div>
:<div className="fig4">{characterViews.map(view => <div key={view.id}>
<WardrobeFigure selection={outfitPreview(look.config)} character={look.config.wardrobe?.character || 'female'} view={view.id} label={`${look.name}, góc ${view.label}`}/>
<span className="muted">{view.label}</span>
</div>)}</div>}
</div>
<div className="final-details"><span className="eyebrow">BẢN PHỐI CỦA BẠN</span><h2>{look.name}</h2><div className="tags"><span>{look.outfitName}</span><span>{look.styleName}</span><span>{look.eventName}</span></div><div className="final-scores">{[['Style Match',look.matchScore??styleMatch],['Cultural Score',review?.current.scoreCard?.total??look.culturalScore],['Color Harmony',look.colorHarmony??harmony]].map(([label,value])=><div key={label}><span>{label}</span><strong>{value === null || value === undefined ? (reviewBusy ? 'Đang chấm…' : 'Chưa có dữ liệu') : value + '%'}</strong><div className="score-track"><i style={{width:`${Math.max(0,Math.min(100,Number(value ?? 0)))}%`}}/></div></div>)}</div><div className="final-actions"><button className="button primary" onClick={save}>{saved?<Check size={18}/>:<Heart size={18}/>} {saved?'Đã lưu look':'Lưu look'}</button><button className="button outline" onClick={share} disabled={sharing}><Share2 size={17}/> Chia sẻ</button>{look.config.wardrobe&&<button className="button outline" onClick={()=>setDialog(true)}><BookOpen size={17}/> Checklist &amp; Lookbook</button>}</div><p className="form-note">Lưu trên trình duyệt này. Chia sẻ bằng liên kết look.</p>{notice&&<div className="share-notice" role="status">{notice}<input aria-label="Liên kết look" readOnly value={window.location.href} onFocus={e=>e.target.select()}/></div>}<button className="text-button back-link" onClick={()=>{update({mix:look.config});navigate(`/mix/${encodeURIComponent(look.config.conceptId)}`);}}><ArrowLeft size={17}/> Remix lại bản phối</button></div></div>{look.config.wardrobe&&<><StylistReview review={review} busy={reviewBusy} error={reviewError} retry={()=>setReviewRetry(v=>v+1)}/>
<ShareDialog open={dialog} onClose={()=>setDialog(false)} selection={normalizeMaleSelection(look.config.wardrobe.selection,look.config.wardrobe.character)} character={look.config.wardrobe.character}
  note={noteOf(review)} extras={{...extras,styleName:look.styleName,eventName:look.eventName}} name={look.outfitName}/></>}
<section className="knowledge-section"><div><span className="eyebrow"><BookOpen size={18}/> BẠN ĐANG MẶC GÌ?</span><h2>{knowledge?.name||look.outfitName}</h2><p>Hiểu câu chuyện.<br/>Thêm yêu trang phục.</p></div><div>{cultureError?<ErrorBox message={cultureError} retry={()=>setCultureRetry(v=>v+1)}/>:knowledge?<CulturalContent knowledge={knowledge}/>:<Loading text="Đang tải câu chuyện trang phục…"/>}</div></section><div className="center"><Link className="button outline" to="/stylist">Bắt đầu một cảm hứng mới <Sparkles size={17}/></Link></div></>}</main>;
}
