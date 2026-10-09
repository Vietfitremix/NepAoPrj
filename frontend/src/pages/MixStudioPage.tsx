import { useEffect, useRef, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { ArrowLeft, ArrowRight, RotateCcw, SlidersHorizontal, Sparkles } from 'lucide-react';
import { useSession } from '../state';
import type { CulturalResult, MixConfig, Outfit } from '../types';
import { getOutfits } from '../services/outfitApi';
import { getCulturalScore } from '../services/culturalApi';
import { applyChanges } from '../services/remixApi';
import { wardrobeRemix } from '../services/aiApi';
import type { WardrobeRemix } from '../services/aiApi';
import RemixPanel from '../components/mix/RemixPanel';
import { createLook } from '../services/lookApi';
import { errorMessage } from '../services/api';
import { EmptyState, ErrorBox, Loading, PageHeading, Stepper } from '../components/common/UI';
import { ChoiceGroup } from '../components/mix/Selectors';
import WardrobeControls from '../components/mix/WardrobeControls';
import Avatar2D from '../components/mix/Avatar2D';
import CulturalScore from '../components/cultural/CulturalScore';
import { configureWardrobe, initialWardrobe } from '../utils/mixWardrobe';
import type { MaleSelection, WardrobeCharacter } from '../utils/maleWardrobe';
import { events } from './StylistPage';
import { reviewContext } from '../utils/outfitContext';

export default function MixStudioPage() {
  const {conceptId}=useParams();
  const {session,update}=useSession();
  const navigate=useNavigate();
  const config=session.mix?.conceptId===conceptId?session.mix:undefined;
  const concept=session.recommendation?.concepts.find(item=>item.id===conceptId);
  const [outfits,setOutfits]=useState<Outfit[]>();
  const [outfitError,setOutfitError]=useState('');
  const [retry,setRetry]=useState(0);
  const [scoreRetry,setScoreRetry]=useState(0);
  const [score,setScore]=useState<{key:string;value:CulturalResult}>();
  const [scoreError,setScoreError]=useState('');
  const [checking,setChecking]=useState(false);
  const [prompt,setPrompt]=useState('');
  const [busy,setBusy]=useState<'remix'|'generate'|''>('');
  const [error,setError]=useState('');
  const [remixResult,setRemixResult]=useState<WardrobeRemix>();
  const key=JSON.stringify(config);
  const contextKey=JSON.stringify(reviewContext(session.preferences?.answers));
  const scoreKey=key+contextKey;
  const latestKey=useRef(key);latestKey.current=key;
  const active=useRef(true);
  useEffect(()=>{active.current=true;return()=>{active.current=false;};},[]);
  useEffect(()=>{
    const controller=new AbortController();setOutfits(undefined);setOutfitError('');
    getOutfits(controller.signal).then(data=>{if(!controller.signal.aborted)setOutfits(data);})
      .catch(err=>{if(!controller.signal.aborted)setOutfitError(errorMessage(err));});
    return()=>controller.abort();
  },[retry]);
  useEffect(()=>{
    if(!config?.wardrobe || !outfits)return;
    const normalized=configureWardrobe(config,config.wardrobe.selection,config.wardrobe.character,outfits);
    if(JSON.stringify(normalized)!==key)update({mix:normalized});
  },[key,outfits]);
  useEffect(()=>{
    if(!config || !outfits)return;
    // Restore old selections before asking the API to validate or score them.
    if(config.wardrobe && JSON.stringify(configureWardrobe(config,config.wardrobe.selection,config.wardrobe.character,outfits))!==key)return;
    const controller=new AbortController();setChecking(true);setScoreError('');
    const timer=setTimeout(()=>{
      getCulturalScore(config,controller.signal,session.preferences?.answers).then(value=>{if(!controller.signal.aborted)setScore({key:scoreKey,value});})
        .catch(err=>{if(!controller.signal.aborted)setScoreError(errorMessage(err));})
        .finally(()=>{if(!controller.signal.aborted)setChecking(false);});
    },450);
    return()=>{clearTimeout(timer);controller.abort();};
  },[key,contextKey,scoreRetry,outfits]);
  if(!config)return <main className="page-container nepao-page"><EmptyState title="Chọn một concept để bắt đầu mix">Bản phối chưa có trong phiên này. Hãy tạo concept để khám phá Mix Studio.</EmptyState></main>;
  const outfit=outfits?.find(item=>item.code===config.outfitCode);
  const wardrobe=config.wardrobe || initialWardrobe(config,session.preferences?.character || 'female');
  function change(patch:Partial<MixConfig>){if(!config)return;update({mix:{...config,...patch}});setError('');setRemixResult(undefined);}
  function chooseWardrobe(selection:MaleSelection,character:WardrobeCharacter){
    if(!config || !outfits)return;
    change(configureWardrobe(config,selection,character,outfits));
  }
  function reset(){
    if(!concept || !config)return;
    const original:MixConfig={conceptId:config.conceptId,outfitCode:concept.outfitCode,colorCode:concept.colorCode,
      styleCode:concept.styleCode,accessoryCodes:concept.accessoryCodes || [],eventCode:session.preferences?.eventCode || 'TET'};
    original.wardrobe=initialWardrobe(original,session.preferences?.character || 'female');
    change(original);
  }
  async function doRemix(event:React.FormEvent){
    event.preventDefault();if(!config || !prompt.trim() || busy)return;
    const requestKey=key;setBusy('remix');setError('');
    try{
      const result=await wardrobeRemix(config,prompt.trim(),session.preferences?.answers);
      if(!active.current || latestKey.current!==requestKey)return;
      if(result.applied)chooseWardrobe(result.selection,wardrobe.character);
      setRemixResult(result);setPrompt('');
    }catch(err){if(active.current)setError(errorMessage(err));}
    finally{if(active.current)setBusy('');}
  }
  async function generate(){
    if(!config || busy || checking || score?.key!==scoreKey)return;
    setBusy('generate');setError('');
    try{
      const look=await createLook(config,session.preferences?.answers);
      if(!look.id)throw new Error('Máy chủ chưa trả về mã look. Vui lòng thử lại.');
      if(active.current)navigate(`/look/${encodeURIComponent(look.id)}`);
    }catch(err){if(active.current)setError(errorMessage(err));}
    finally{if(active.current)setBusy('');}
  }
  return <main className="page-container studio-page nepao-page wide">
    <Stepper active={2}/><PageHeading eyebrow="YOUR STYLE – YOUR STORY" title="Một chút remix – Một chất riêng." description="Đổi trang phục, phối quần váy, giày dép, màu, họa tiết và mọi phụ kiện trong tủ đồ của bạn."/>
    <div className="studio-toolbar"><Link to="/concepts" className="text-button"><ArrowLeft size={16}/> Chọn lại concept</Link>
      <span>{concept?.name || 'Bản phối của bạn'}</span>
      {concept&&<button className="text-button" disabled={!!busy} onClick={reset}><RotateCcw size={15}/> Về bản gốc</button>}
    </div>
    {outfitError?<ErrorBox message={outfitError} retry={()=>setRetry(value=>value+1)}/>:!outfit?<Loading text="Đang tải trang phục và phụ kiện…"/>:<>
      <div className="studio">
        <Avatar2D outfit={outfit} config={{...config,wardrobe}}/>
        <section className="panel controls controls-panel">
          <div className="small-panel-heading"><SlidersHorizontal size={19}/><h2>Tùy chỉnh</h2></div>
          <WardrobeControls character={wardrobe.character} selection={wardrobe.selection} onChange={chooseWardrobe} disabled={!!busy}/>
          <ChoiceGroup label="Phong cách" options={outfit.styles} value={config.styleCode} onChange={styleCode=>change({styleCode})} disabled={!!busy}/>
          <ChoiceGroup label="Bối cảnh" options={events} value={config.eventCode} onChange={eventCode=>change({eventCode})} disabled={!!busy}/>
          <p className="form-note">Cultural Check tự cập nhật theo bản phối: áo, màu tự chọn, quần/váy, giày, phụ kiện, họa tiết và bối cảnh. Các món hiện đại được xét theo phong cách bạn chọn.</p>
        </section>
        <CulturalScore result={score?.key===scoreKey?score.value:undefined} busy={checking || (!scoreError && score?.key!==scoreKey)} error={scoreError}
          retry={()=>setScoreRetry(value=>value+1)} apply={changes=>{update({mix:applyChanges(config,changes)});setRemixResult(undefined);setError('');}} disabled={!!busy}/>
      </div>
      <form className="remix-bar" onSubmit={doRemix}><Sparkles size={22}/><label className="sr-only" htmlFor="remix">Yêu cầu AI remix</label>
        <input id="remix" value={prompt} disabled={!!busy} maxLength={1500} onChange={event=>setPrompt(event.target.value)} placeholder="Cho outfit trẻ hơn nhưng vẫn giữ màu đỏ…"/>
        <button className="button dark" disabled={!!busy || !prompt.trim()}>{busy==='remix'?'Đang remix…':'AI Remix'}<Sparkles size={16}/></button>
      </form>
      {remixResult&&<RemixPanel result={remixResult} disabled={!!busy} onPick={option=>{chooseWardrobe(option.selection,wardrobe.character);setRemixResult(undefined);}}/>}
      {error&&<ErrorBox message={error}/>}
      <div className="generate-row"><p>Bản phối đã đúng chất bạn?<br/><span>Tạo look để lưu lại và chia sẻ câu chuyện của mình.</span></p>
        <button className="button primary" onClick={generate} disabled={!!busy || checking || !!scoreError || score?.key!==scoreKey}>{busy==='generate'?'Đang tạo look…':'Generate look'}<ArrowRight size={19}/></button>
      </div>
    </>}
  </main>;
}
