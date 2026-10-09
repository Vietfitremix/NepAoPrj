import { useEffect, useRef, useState } from 'react';
import { X } from 'lucide-react';
import type { MaleSelection, WardrobeCharacter } from '../../utils/maleWardrobe';
import { checklistItems, checklistText, downloadCanvas, drawChecklist, drawLookbook, noMark } from '../../utils/lookbook';
import type { LookbookExtras, ReviewNote } from '../../utils/lookbook';
import { ScoreMini } from './ScoreCard';

/** Hộp thoại Checklist "soi và mặc theo" + thẻ Lookbook (vẽ trên trình duyệt, không tải lên máy chủ). */
export default function ShareDialog({ open, onClose, selection, character, note, extras, name }: {
  open: boolean; onClose: () => void; selection: MaleSelection; character: WardrobeCharacter; note: ReviewNote; extras: LookbookExtras; name: string;
}) {
  const ref = useRef<HTMLDialogElement>(null);
  const [img, setImg] = useState(''); const [cv, setCv] = useState<HTMLCanvasElement | null>(null);
  const [copy, setCopy] = useState('Sao chép chữ'); const [error, setError] = useState('');
  const items = checklistItems(selection, character, extras.tips);
  const key = JSON.stringify([selection, character, note.title, note.comment, note.card?.total, extras.tips]);
  useEffect(() => {
    const d = ref.current; if (!d) return;
    if (open && !d.open) d.showModal();
    if (!open && d.open) d.close();
  }, [open]);
  useEffect(() => {
    if (!open) return;
    let live = true; setImg(''); setCv(null); setError('');
    drawLookbook(selection, character, note, extras)
      .then(c => { if (live) { setCv(c); setImg(c.toDataURL('image/png')); } })
      .catch(() => { if (live) setError('Chưa vẽ được thẻ Lookbook. Vui lòng thử lại.'); });
    return () => { live = false; };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open, key]);
  const slug = noMark(`${name}-${character}`).replace(/[^a-zA-Z0-9]+/g, '-').toLowerCase();
  function printList() {
    const w = window.open('', '_blank'); if (!w) return;
    const rows = items.map(it => `<li><span class="g">${it.group}</span><div><b>${it.name}</b>${it.color ? ` ● ${it.color.name} ${it.color.hex}` : ''}${it.tip ? `<div class="m">${it.tip}</div>` : ''}</div></li>`).join('');
    w.document.write(`<!doctype html><meta charset="utf-8"><title>Checklist Nếp Áo</title><style>body{font:16px/1.5 system-ui,sans-serif;margin:32px;color:#2b2b2b}h1{color:#8b2e1f;font-size:22px}ol{padding:0;list-style:none}li{margin:10px 0;display:grid;grid-template-columns:7.5em 1fr;gap:8px}.g{font-size:12px;color:#6b645a;text-transform:uppercase}.m{color:#6b645a;font-size:14px}</style><h1>Nếp Áo – Checklist bản phối</h1><ol>${rows}</ol>`);
    w.document.close(); w.focus(); w.print();
  }
  return <dialog ref={ref} className="share-dlg" onClose={onClose} onCancel={onClose} onClick={e => { if (e.target === e.currentTarget) onClose(); }}>
    <button className="share-x" aria-label="Đóng" onClick={onClose}><X size={20}/></button>
    <div className="share">
      <div>
        <h3>Checklist soi và mặc theo</h3>
        <ol className="ck">{items.map((it, i) => <li key={i}><span className="ck-g">{it.group}</span><div><b>{it.name}</b>
          {it.color && <> <span className="ck-sw" style={{ background: it.color.hex }}/> {it.color.name} <span className="muted">{it.color.hex}</span></>}
          {!it.color && it.detail && <span className="muted"> · {it.detail}</span>}
          {it.tip && <div className="muted">{it.tip}</div>}</div></li>)}</ol>
        {note.card && <p><ScoreMini card={note.card}/></p>}
        {note.tip && <p className="recommend"><b>Recommend:</b> {note.tip}</p>}
        <div className="row">
          <button className="button outline" onClick={printList}>In checklist</button>
          <button className="button outline" onClick={async () => { try { await navigator.clipboard.writeText(checklistText(items, note)); setCopy('Đã sao chép ✓'); } catch { setCopy('Không sao chép được'); } setTimeout(() => setCopy('Sao chép chữ'), 1600); }}>{copy}</button>
          <button className="button outline" onClick={async () => downloadCanvas(await drawChecklist(selection, character, note, extras), `nep-ao-checklist-${slug}.png`)}>Tải ảnh checklist</button>
        </div>
      </div>
      <div className="lb-col">
        <h3>Thẻ Lookbook</h3>
        <div className="lb">{img ? <img src={img} alt="Thẻ Lookbook"/> : <p className="muted">{error || 'Đang vẽ thẻ…'}</p>}</div>
        {!note.comment && <p className="muted">Chờ stylist nhận xét xong để thẻ có thêm tên bộ và lời stylist.</p>}
        <button className="button primary" disabled={!cv} onClick={() => cv && downloadCanvas(cv, `nep-ao-lookbook-${slug}.png`)}>Tải thẻ Lookbook (PNG)</button>
      </div>
    </div>
    <div className="share-foot"><span className="muted">Ảnh được tạo ngay trên máy bạn, không tải lên máy chủ.</span><button className="button outline" onClick={onClose}>Đóng</button></div>
  </dialog>;
}
