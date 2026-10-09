import type { Accessory, Option } from '../../types';
export function ChoiceGroup({ label, options, value, onChange, disabled = false }: { label: string; options: Option[]; value: string; onChange: (value: string) => void; disabled?: boolean }) {
  return <fieldset className="choice-group" disabled={disabled}><legend>{label}</legend><div className="chips">{options.map(option => <button type="button" key={option.code} className={`chip ${value === option.code ? 'selected' : ''}`} aria-pressed={value === option.code} onClick={() => onChange(option.code)}>{option.label}</button>)}</div></fieldset>;
}
export function ColorSelector({ options, value, onChange, disabled }: { options: Option[]; value: string; onChange: (value: string) => void; disabled?: boolean }) {
  return <fieldset className="choice-group" disabled={disabled}><legend>Màu sắc <span>{options.find(o=>o.code===value)?.label}</span></legend><div className="color-options">{options.map(option=><button type="button" key={option.code} className={`color-swatch ${value===option.code?'selected':''}`} style={{background:option.hex || '#ddd'}} title={option.label} aria-label={option.label} aria-pressed={value===option.code} onClick={()=>onChange(option.code)}>{value===option.code?'✓':''}</button>)}</div></fieldset>;
}
const CATEGORIES: { type: string; label: string }[] = [
  { type: 'BOTTOM', label: 'Quần & Váy phối' },
  { type: 'HEADWEAR', label: 'Mũ nón & Khăn' },
  { type: 'JEWELRY', label: 'Trang sức & Kiềng' },
  { type: 'FOOTWEAR', label: 'Giày dép & Guốc hài' },
  { type: 'ACCESSORY', label: 'Phụ kiện cầm tay' }
];

export function AccessorySelector({ options, values, onChange, disabled }: { options: Accessory[]; values: string[]; onChange: (values: string[])=>void; disabled?: boolean }) {
  if (!options.length) {
    return <fieldset className="choice-group" disabled={disabled}><legend>Món đồ & Phụ kiện phối</legend><p className="muted">Chưa có phụ kiện cho trang phục này.</p></fieldset>;
  }

  // Group accessories by their type
  const grouped = CATEGORIES.map(cat => ({
    ...cat,
    items: options.filter(o => (o.type || 'ACCESSORY') === cat.type)
  })).filter(g => g.items.length > 0);

  // Fallback for any accessory with unknown type
  const knownTypes = new Set(CATEGORIES.map(c => c.type));
  const otherItems = options.filter(o => !knownTypes.has(o.type || ''));
  if (otherItems.length) {
    grouped.push({ type: 'OTHER', label: 'Khác', items: otherItems });
  }

  return (
    <fieldset className="choice-group" disabled={disabled}>
      <legend>Món đồ & Phụ kiện phối <span>({values.length} đã chọn)</span></legend>
      <div className="accessory-groups" style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
        {grouped.map(group => (
          <div key={group.type} className="accessory-group" style={{ borderTop: '1px dashed #e2e4d8', paddingTop: '8px' }}>
            <div style={{ fontSize: '11px', fontWeight: 650, color: '#4a6349', marginBottom: '6px', display: 'flex', alignItems: 'center', gap: '5px' }}>
              <span>{group.label}</span>
              <span style={{ fontSize: '10px', color: '#88927f', fontWeight: 400 }}>({group.items.length})</span>
            </div>
            <div className="accessory-list">
              {group.items.map(option => (
                <label key={option.code} title={option.description || option.label}>
                  <input
                    type="checkbox"
                    checked={values.includes(option.code)}
                    onChange={e => onChange(e.target.checked ? [...values, option.code] : values.filter(v => v !== option.code))}
                  />
                  <span>{option.label}</span>
                </label>
              ))}
            </div>
          </div>
        ))}
      </div>
    </fieldset>
  );
}
