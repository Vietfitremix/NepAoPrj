import { useEffect, useRef, useState } from 'react';

import { Check, Download, RotateCcw, RotateCw, Shirt } from 'lucide-react';
import { ErrorBox, PageHeading } from '../components/common/UI';
import { assetRoot, characters, getWardrobe, selectionKey, characterSelectionKey, normalizeCharacter, normalizeMaleSelection, readMaleSelection, accessorySlots, selectedWardrobeItems } from '../utils/maleWardrobe';
import type { AccessorySlot } from '../utils/maleWardrobe';
import type { MaleSelection, WardrobeCharacter } from '../utils/maleWardrobe';
import { renderMaleCharacter,characterHeadroom } from '../utils/renderMaleCharacter';
import { withHandForeground } from '../utils/sourceDirectionRenderer';
import type { CharacterImages } from '../utils/sourceDirectionRenderer';

import { characterViews, characterViewKey, normalizeView, rotateView, characterBaseFile, directionalGarmentFile, leftGarmentSourceFile } from '../utils/characterViews';
import type { CharacterView } from '../utils/characterViews';
import { wardrobeColors,wardrobePatterns,patternFile } from '../utils/wardrobeStyles';
import type { GarmentStyle,GarmentStyleSlot } from '../utils/wardrobeStyles';

function initialSelection(character: WardrobeCharacter) {
  try { return readMaleSelection(localStorage.getItem(selectionKey(character)), character); }
  catch { return normalizeMaleSelection(null, character); }
}

export default function MaleStudioPage({ initialCharacter }: { initialCharacter?: WardrobeCharacter }) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const imageCache = useRef<Record<string, HTMLImageElement>>({});
  const handCache = useRef<Partial<Record<WardrobeCharacter, CharacterImages>>>({});
  const dragStart = useRef<{x:number;y:number}|null>(null);
  const [view,setView] = useState<CharacterView>(() => {
    try { return normalizeView(localStorage.getItem(characterViewKey)); } catch { return 'front'; }
  });
  const [baseViewMode,setBaseViewMode] = useState(false);
  const [tab,setTab] = useState<'shirt'|'pants'|'shoes'|'acc'>('shirt');
  const [character, setCharacter] = useState<WardrobeCharacter>(() => {
    if (initialCharacter) return initialCharacter;
    try { return normalizeCharacter(localStorage.getItem(characterSelectionKey)); }
    catch { return 'male'; }
  });
  const [selection, setSelection] = useState(() => initialSelection(character));
  const maleWardrobe = getWardrobe(character);
  const maleAssetRoot = assetRoot(character);
  const [images, setImages] = useState<CharacterImages>();
  const [error, setError] = useState('');
  const [retry, setRetry] = useState(0);
  const [exporting, setExporting] = useState(false);
  const [notice, setNotice] = useState('');
  const outfit = maleWardrobe.outfits.find(item => item.id === selection.shirt);
  const pants = maleWardrobe.pants.find(item => item.id === selection.pants);
  const description = selectedWardrobeItems(selection,character).map(item=>item.name).join(', ') || 'Nhân vật nền';
  const characterName = character === 'female' ? 'nữ' : 'nam';
  const viewLabel = characterViews.find(item=>item.id===view)!.label;
  const showingBase = baseViewMode;

  useEffect(() => {
    try { localStorage.setItem(characterViewKey,view); } catch { /* Storage is optional. */ }
  },[view]);

  useEffect(() => {
    try { localStorage.setItem(characterSelectionKey, character); } catch { /* Storage is optional. */ }
  }, [character]);

  useEffect(() => {
    let cancelled = false;
    setError('');
    setImages(undefined);
    const selectedItems = selectedWardrobeItems(selection,character);
    const files = [
      ...characterViews.map(item => characterBaseFile(character, item.id)),
      ...selectedItems.flatMap(item => characterViews.map(v => directionalGarmentFile(item.file, v.id))),
      ...selectedItems.filter(item=>maleWardrobe.outfits.includes(item)).map(item=>leftGarmentSourceFile(item.reference)),
      ...Object.values(selection.styles??{}).map(patternFile).filter((file):file is string=>!!file),
    ];
    Promise.all([...new Set(files)].map(file => new Promise<[string, HTMLImageElement]>((resolve, reject) => {
      const cacheKey = file.startsWith('patterns/')?file:character + '/' + file;
      const cached = imageCache.current[cacheKey];
      if (cached) { resolve([file, cached]); return; }
      const image = new Image();
      image.onload = () => { imageCache.current[cacheKey] = image; resolve([file, image]); };
      image.onerror = () => reject(new Error('Không tải được trang phục. Vui lòng thử lại.'));
      image.src = file.startsWith('/api/assets/')?file:(file.startsWith('patterns/')?'/figure/':maleAssetRoot) + file;
    }))).then(entries => {
      if (!cancelled) {
        const loaded = Object.fromEntries(entries);
        const hands = handCache.current[character];
        const completeHands=hands&&characterViews.every(v=>hands[`views/base-bottom-shoes-${v.id}.png`]);
        const fitted = completeHands ? { ...loaded, ...hands } : withHandForeground(loaded, character);
        handCache.current[character] = Object.fromEntries(Object.entries(fitted).filter(([file]) => file.startsWith('views/hands-') || file.startsWith('views/base-')));
        setImages(fitted);
      }
    }).catch((err: unknown) => {
      if (!cancelled) setError(err instanceof Error ? err.message : 'Không tải được trang phục.');
    });
    return () => { cancelled = true; };
  }, [retry, character, selection.shirt, selection.pants, selection.shoes, selection.accessories, selection.styles]);

  useEffect(() => {
    const context = canvasRef.current?.getContext('2d');
    if (!context) return;
    context.clearRect(0, 0, maleWardrobe.width, maleWardrobe.height);
    if (!images) return;
    renderMaleCharacter(context, images, showingBase?{shirt:null,pants:null,shoes:null}:selection, character, view);
  }, [images, selection, character, view, showingBase]);

  function chooseView(value: CharacterView) {
    setView(value);
    setNotice('');
  }

  function chooseCharacter(value: WardrobeCharacter) {
    if (value === character) return;
    setImages(undefined);
    setCharacter(value);
    setSelection(initialSelection(value));
    setNotice('');
  }

  function choose(patch: Partial<MaleSelection>) {
    const value = { ...selection, ...patch };
    setSelection(value);
    setBaseViewMode(false);
    setNotice('');
    try { localStorage.setItem(selectionKey(character), JSON.stringify(value)); } catch { /* Keep the selection in memory. */ }
  }

  function chooseAccessory(slot:AccessorySlot,id:string|null) {
    choose({accessories:{...selection.accessories,[slot]:id}});
  }

  function chooseStyle(slot:GarmentStyleSlot,patch:GarmentStyle) {
    choose({styles:{...selection.styles,[slot]:{...selection.styles?.[slot],...patch}}});
  }

  function styleControls(slot:GarmentStyleSlot,label:string,selected:boolean) {
    const style=selection.styles?.[slot];
    const pattern=wardrobePatterns.find(item=>item.id===style?.pattern);
    return <fieldset className="wardrobe-style-controls" disabled={!images||exporting||!selected}>
      <legend>Màu và họa tiết {label}</legend>
      <div className="wardrobe-color-options" role="group" aria-label={`Màu ${label}`}>
        <button type="button" className={`wardrobe-color-original ${!style?.color?'selected':''}`} aria-pressed={!style?.color} onClick={()=>chooseStyle(slot,{color:null})}>Màu gốc</button>
        {wardrobeColors.map(color=><button key={color.value} type="button" className={`wardrobe-color-swatch ${style?.color===color.value?'selected':''}`} style={{backgroundColor:color.value}} title={color.name} aria-label={`${label}: ${color.name}`} aria-pressed={style?.color===color.value} onClick={()=>chooseStyle(slot,{color:color.value})}/>)}
        <label className="wardrobe-custom-color">Tự chọn<input type="color" aria-label={`Tự chọn màu ${label}`} value={style?.color||'#b52838'} onChange={event=>chooseStyle(slot,{color:event.target.value})}/></label>
      </div>
      <label className="wardrobe-pattern-select">Họa tiết<select aria-label={`Họa tiết ${label}`} value={style?.pattern||''} onChange={event=>chooseStyle(slot,{pattern:event.target.value||null})}>
        <option value="">Giữ họa tiết gốc</option>{wardrobePatterns.map(item=><option key={item.id} value={item.id}>{item.name}</option>)}
      </select></label>
      {pattern&&<div className="wardrobe-pattern-preview"><img src={'/figure/'+pattern.thumbnail} alt=""/><span>{pattern.name}</span></div>}
    </fieldset>;
  }

  function download() {
    const canvas = canvasRef.current;
    if (!canvas || !images || exporting) return;
    setExporting(true);
    setNotice('');
    try {
      canvas.toBlob(blob => {
        setExporting(false);
        if (!blob) { setNotice('Chưa xuất được ảnh. Vui lòng thử lại.'); return; }
        const url = URL.createObjectURL(blob);
        const anchor = document.createElement('a');
        anchor.href = url;
        const itemIds=selectedWardrobeItems(selection,character).map(item=>item.id).join('-');
        anchor.download = showingBase ? `viet-fit-${character}-base-${view}.png` : `viet-fit-${character}-${itemIds || 'base'}-${view}.png`;
        anchor.click();
        setTimeout(() => URL.revokeObjectURL(url), 1000);
        setNotice('Ảnh PNG đã sẵn sàng tải xuống.');
      }, 'image/png');
    } catch {
      setExporting(false);
      setNotice('Chưa xuất được ảnh. Vui lòng thử lại.');
    }
  }

  return <main className="page-container male-studio-page">
    <PageHeading eyebrow="VIỆT FIT / STUDIO 3D" title="Chọn áo – Phối đồ – Chất riêng." description="Chọn trang phục và phụ kiện riêng cho nhân vật ở mọi hướng."/>
    <div className="male-studio-layout">
      <section className="male-character-stage" aria-busy={!images && !error}>
        <div className="male-character-heading"><span>NHÂN VẬT {characterName.toUpperCase()}</span><span>GÓC {viewLabel.toUpperCase()}</span></div>
        <div className="character-view-controls" role="group" aria-label="Chọn hướng nhân vật" onKeyDown={event=>{
          if(event.key==='ArrowLeft'||event.key==='ArrowRight'){
            event.preventDefault();chooseView(rotateView(view,event.key==='ArrowLeft'?-1:1));
          }
        }}>
          <button type="button" className="character-turn-button" aria-label="Xoay trái 90 độ" disabled={exporting} onClick={()=>chooseView(rotateView(view,-1))}><RotateCcw size={17}/></button>
          {characterViews.map(item=><button type="button" key={item.id} className={`character-view-button ${view===item.id?'selected':''}`} aria-pressed={view===item.id} disabled={exporting} onClick={()=>chooseView(item.id)}>{item.label}</button>)}
          <button type="button" className="character-turn-button" aria-label="Xoay phải 90 độ" disabled={exporting} onClick={()=>chooseView(rotateView(view,1))}><RotateCw size={17}/></button>
        </div>
        <canvas ref={canvasRef} width={maleWardrobe.width} height={maleWardrobe.height+characterHeadroom} role="img" aria-label={`Nhân vật ${characterName}, góc ${viewLabel.toLowerCase()}: ${showingBase?'Nhân vật nền':description}`}
          onPointerDown={event=>{dragStart.current={x:event.clientX,y:event.clientY};}}
          onPointerUp={event=>{
            const start=dragStart.current;dragStart.current=null;
            if(!start||exporting)return;
            const dx=event.clientX-start.x,dy=event.clientY-start.y;
            if(Math.abs(dx)>45&&Math.abs(dx)>Math.abs(dy)*1.5)chooseView(rotateView(view,dx<0?1:-1));
          }}
          onPointerCancel={()=>{dragStart.current=null;}}/>
        {!images && !error && <p className="male-stage-status" role="status">Đang chuẩn bị nhân vật và trang phục…</p>}
        {error && <div className="male-stage-status"><ErrorBox message={error} retry={() => setRetry(value => value + 1)}/></div>}
        <p className="male-outfit-caption" aria-live="polite">{showingBase?'Nhân vật nền':outfit?.name || 'Áo nền'}<small>{`Góc ${viewLabel.toLowerCase()} · ` + (showingBase ? 'Dáng nhân vật nền' : (pants?.name || 'Quần nền'))}</small></p>
      </section>
      <section className="panel male-wardrobe-panel">
        <div className="small-panel-heading"><Shirt size={20}/><h2>Tủ đồ của bạn</h2></div>
        <p className="muted">Chọn riêng áo, quần, giày và từng nhóm phụ kiện. Xoay nhân vật giữ nguyên bộ đồ đang mặc.</p>
        {showingBase&&<div className="character-view-note">Bạn đang xem dáng nhân vật nền ở 4 hướng. Chọn áo, quần hoặc giày để mặc trang phục ở mọi góc nhìn 3D.
          <button type="button" className="text-button" disabled={exporting} onClick={()=>{setSelection(initialSelection(character));setBaseViewMode(false);}}>Mặc lại bộ đồ</button>
        </div>}
        <h3 className="male-wardrobe-category">Nhân vật</h3>
        <div className="chips character-options" role="group" aria-label="Chọn nhân vật">
          {characters.map(item => <button key={item.id} className={`chip ${character === item.id ? 'selected' : ''}`} aria-pressed={character === item.id} disabled={!images || exporting} onClick={() => chooseCharacter(normalizeCharacter(item.id))}>{item.name}</button>)}
        </div>
        <div className="wardrobe-tabs" role="tablist" aria-label="Nhóm trang phục">
          {([['shirt','Áo'],['pants',character==='female'?'Quần / Váy':'Quần'],['shoes','Giày'],['acc','Phụ kiện']] as const).map(([id,label])=><button key={id} type="button" role="tab" aria-selected={tab===id} className={tab===id?'on':''} onClick={()=>setTab(id)}>{label}</button>)}
        </div>
        <div hidden={tab!=='shirt'}>
        <h3 className="male-wardrobe-category">Áo</h3>
        <div className="male-outfit-options" role="group" aria-label="Chọn áo">
          {maleWardrobe.outfits.map(item => <button key={item.id} type="button" className={`male-outfit-card ${selection.shirt === item.id ? 'selected' : ''}`} aria-pressed={selection.shirt === item.id} disabled={!images || exporting} onClick={() => choose({ shirt: item.id })}>
            <span className="male-outfit-thumbnail"><img src={maleAssetRoot + item.thumbnail} alt=""/></span>
            <span className="male-outfit-copy"><strong>{item.name}</strong><small>{item.detail}</small></span>
            {selection.shirt === item.id && <Check size={18} aria-hidden="true"/>}
          </button>)}
        </div>
        <button className="text-button male-remove-button" disabled={!images || exporting} aria-pressed={selection.shirt === null} onClick={() => choose({ shirt: null })}>Dùng áo nền</button>
        {styleControls('shirt','áo',!!outfit)}
        </div>
        <div hidden={tab!=='pants'}>
        <h3 className="male-wardrobe-category">{character === 'female' ? 'Quần / Váy' : 'Quần'}</h3>
        <div className="male-outfit-options" role="group" aria-label={character === 'female' ? 'Chọn quần hoặc váy' : 'Chọn quần'}>
          {maleWardrobe.pants.map(item => <button key={item.id} type="button" className={`male-outfit-card ${selection.pants === item.id ? 'selected' : ''}`} aria-pressed={selection.pants === item.id} disabled={!images || exporting} onClick={() => choose({ pants: item.id })}>
            <span className="male-outfit-thumbnail"><img src={maleAssetRoot + item.thumbnail} alt=""/></span>
            <span className="male-outfit-copy"><strong>{item.name}</strong><small>{item.detail}</small></span>
            {selection.pants === item.id && <Check size={18} aria-hidden="true"/>}
          </button>)}
        </div>
        <button className="text-button male-remove-button" disabled={!images || exporting} aria-pressed={selection.pants === null} onClick={() => choose({ pants: null })}>Dùng quần nền</button>
        {styleControls('pants',character==='female'?'quần / váy':'quần',!!pants)}
        </div>
        <div hidden={tab!=='shoes'}>
        <h3 className="male-wardrobe-category">Giày</h3>
        <div className="male-outfit-options" role="group" aria-label="Chọn giày">
          {maleWardrobe.shoes.map(item => <button key={item.id} className={`male-outfit-card ${selection.shoes === item.id ? 'selected' : ''}`} aria-pressed={selection.shoes === item.id} disabled={!images || exporting} onClick={() => choose({shoes:item.id})}>
            <span className="male-outfit-thumbnail"><img src={maleAssetRoot + item.thumbnail} alt=""/></span>
            <span className="male-outfit-copy"><strong>{item.name}</strong><small>{item.detail}</small></span>
          </button>)}
        </div>
        <button className="text-button male-remove-button" disabled={!images || exporting} aria-pressed={!selection.shoes} onClick={() => choose({shoes:null})}>Đi chân trần</button>
        {styleControls('shoes','giày',!!selection.shoes)}
        </div>
        <div hidden={tab!=='acc'}>
        {accessorySlots.map(slot=>{const chosen=maleWardrobe.accessories.find(x=>x.id===selection.accessories?.[slot.id]);return <details key={slot.id} className="acc-slot" open={!!chosen||undefined}>
          <summary><span>{slot.name}</span><small>{chosen?chosen.name:'Chưa chọn'}</small></summary>
          <div className="male-outfit-options" role="group" aria-label={`Chọn ${slot.name.toLowerCase()}`}>
            {maleWardrobe.accessories.filter(item=>item.slot===slot.id).map(item=><button key={item.id} type="button" className={`male-outfit-card ${selection.accessories?.[slot.id]===item.id?'selected':''}`} aria-pressed={selection.accessories?.[slot.id]===item.id} disabled={!images || exporting} onClick={()=>chooseAccessory(slot.id,item.id)}>
              <span className="male-outfit-thumbnail"><img src={maleAssetRoot+item.thumbnail} alt=""/></span>
              <span className="male-outfit-copy"><strong>{item.name}</strong><small>{item.detail}</small></span>
              {selection.accessories?.[slot.id]===item.id&&<Check size={18} aria-hidden="true"/>}
            </button>)}
          </div>
          <button type="button" className="text-button male-remove-button" disabled={!images || exporting} aria-pressed={!selection.accessories?.[slot.id]} onClick={()=>chooseAccessory(slot.id,null)}>Bỏ {slot.name.toLowerCase()}</button>
        </details>;})}
        </div>
        <button className="text-button male-base-button" disabled={!images || exporting} onClick={() => choose({ shirt: null, pants: null, shoes: null, accessories: {}, styles: {} })}><RotateCcw size={16}/> Xem nhân vật nền</button>
        <button className="button primary full-width" disabled={!images || exporting} onClick={download}><Download size={18}/>{exporting ? 'Đang xuất ảnh…' : showingBase?'Tải góc nhìn này':'Tải ảnh đã phối'}</button>
        {notice && <p className="male-download-notice" role="status">{notice}</p>}
      </section>
    </div>
  </main>;
}
