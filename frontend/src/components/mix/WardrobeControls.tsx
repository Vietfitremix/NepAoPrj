import { accessorySlots, assetRoot, getWardrobe, normalizeMaleSelection } from '../../utils/maleWardrobe';
import type { AccessorySlot, MaleSelection, WardrobeCharacter, WardrobeItem } from '../../utils/maleWardrobe';
import { wardrobeColors, wardrobePatterns } from '../../utils/wardrobeStyles';
import type { GarmentStyle, GarmentStyleSlot } from '../../utils/wardrobeStyles';
import { ChoiceGroup } from './Selectors';

export default function WardrobeControls({ character, selection, onChange, disabled }: {
  character: WardrobeCharacter; selection: MaleSelection;
  onChange: (selection: MaleSelection, character: WardrobeCharacter) => void; disabled?: boolean;
}) {
  const catalog=getWardrobe(character);
  const choose=(patch:Partial<MaleSelection>)=>onChange({...selection,...patch},character);
  const style=(slot:GarmentStyleSlot,patch:GarmentStyle)=>choose({styles:{...selection.styles,[slot]:{...selection.styles?.[slot],...patch}}});
  function itemCard(item:WardrobeItem,group:string,selected:boolean,pick:()=>void) {
    return <button type="button" key={item.id} className={`wardrobe-item-card ${selected?'selected':''}`}
      data-wardrobe-item={`${group}:${item.id}`} title={item.detail} aria-pressed={selected} disabled={disabled} onClick={pick}>
      <img loading="lazy" src={assetRoot(character)+item.thumbnail} alt=""/>
      <span>{item.name}</span>
    </button>;
  }
  function styles(slot:GarmentStyleSlot,label:string) {
    const current=selection.styles?.[slot];
    return <fieldset className="wardrobe-style-controls" disabled={disabled || !selection[slot]}>
      <legend>Màu và họa tiết {label}</legend>
      <div className="wardrobe-color-options" role="group" aria-label={`Màu ${label}`}>
        <button type="button" className={`wardrobe-color-original ${!current?.color?'selected':''}`} aria-pressed={!current?.color} onClick={()=>style(slot,{color:null})}>Màu gốc</button>
        {wardrobeColors.map(color=><button type="button" key={color.value} className={`wardrobe-color-swatch ${current?.color===color.value?'selected':''}`}
          style={{backgroundColor:color.value}} aria-label={`${label}: ${color.name}`} title={color.name}
          aria-pressed={current?.color===color.value} onClick={()=>style(slot,{color:color.value})}/>)}
        <label className="wardrobe-custom-color">Tự chọn<input type="color" aria-label={`Tự chọn màu ${label}`} value={current?.color || '#b52838'} onChange={event=>style(slot,{color:event.target.value})}/></label>
      </div>
      <label className="wardrobe-pattern-select">Họa tiết<select aria-label={`Họa tiết ${label}`} value={current?.pattern || ''} onChange={event=>style(slot,{pattern:event.target.value || null})}>
        <option value="">Giữ họa tiết gốc</option>{wardrobePatterns.map(pattern=><option key={pattern.id} value={pattern.id}>{pattern.name}</option>)}
      </select></label>
    </fieldset>;
  }
  const groups:{slot:GarmentStyleSlot;label:string;items:WardrobeItem[];empty?:string}[]=[
    {slot:'shirt',label:'Áo / Trang phục',items:catalog.outfits},
    {slot:'pants',label:'Quần / Váy',items:catalog.pants,empty:'Không phối quần / váy'},
    {slot:'shoes',label:'Giày / Dép',items:catalog.shoes,empty:'Đi chân trần'},
  ];
  const slots=accessorySlots.filter(slot=>catalog.accessories.some(item=>item.slot===slot.id));
  return <div className="mix-wardrobe">
    <ChoiceGroup label="Người mẫu" options={[{code:'female',label:'Nữ'},{code:'male',label:'Nam'}]} value={character}
      disabled={disabled} onChange={value=>{
        const next=value as WardrobeCharacter;
        onChange(normalizeMaleSelection(selection,next),next);
      }}/>
    <p className="form-note">Tủ đồ {character==='male'?'nam':'nữ'}: {catalog.outfits.length} áo, {catalog.pants.length} quần/váy, {catalog.shoes.length} giày/dép và {catalog.accessories.length} phụ kiện. Mỗi vị trí phối một món.</p>
    {groups.map(group=><details className="wardrobe-catalog-group" key={group.slot} open>
      <summary>{group.label}<span>{group.items.length} món</span></summary>
      <div className="wardrobe-item-grid" role="group" aria-label={`Chọn ${group.label.toLowerCase()}`}>
        {group.items.map(item=>itemCard(item,group.slot,selection[group.slot]===item.id,()=>choose({[group.slot]:item.id})))}
      </div>
      {group.empty&&<button type="button" className="text-button wardrobe-clear" disabled={disabled} aria-pressed={!selection[group.slot]} onClick={()=>choose({[group.slot]:null})}>{group.empty}</button>}
      {styles(group.slot,group.slot==='shirt'?'áo':group.slot==='pants'?'quần / váy':'giày')}
    </details>)}
    <h3 className="wardrobe-accessory-heading">Phụ kiện</h3>
    {slots.map(slot=><details className="wardrobe-catalog-group" key={slot.id}>
      <summary>{slot.name}<span>{catalog.accessories.filter(item=>item.slot===slot.id).length} món{selection.accessories?.[slot.id]?' · đã chọn':''}</span></summary>
      <div className="wardrobe-item-grid" role="group" aria-label={`Chọn ${slot.name.toLowerCase()}`}>
        {catalog.accessories.filter(item=>item.slot===slot.id).map(item=>itemCard(item,slot.id,selection.accessories?.[slot.id]===item.id,
          ()=>choose({accessories:{...selection.accessories,[slot.id]:selection.accessories?.[slot.id]===item.id?null:item.id}})))}
      </div>
      <button type="button" className="text-button wardrobe-clear" disabled={disabled} onClick={()=>choose({accessories:{...selection.accessories,[slot.id as AccessorySlot]:null}})}>Bỏ {slot.name.toLowerCase()}</button>
    </details>)}
  </div>;
}
