// Người mẫu giấy: ghép các lớp SVG (thân, quần/váy, áo, phụ kiện) rồi đổi màu #FF0000/#00FF00/#0000FF/#FF00FF thành màu đã chọn.
// Bản chuyển từ playground của AI service (cùng quy ước lớp, hoạ tiết lặp và hoạ tiết đặt vị trí).
import type { Catalog, OutfitState } from './types';

let CAT: Catalog;
export const setCatalog = (c: Catalog) => { CAT = c; };
export const catalog = () => CAT;

export const SLOT_ORDER = ['feet', 'neck', 'jewelry', 'hand', 'hair', 'head'];       // thứ tự lớp: giày → cổ → trang sức → cầm tay → khăn/tóc → nón
export const SLOT_NAME: Record<string, string> = { head: 'Nón', hair: 'Khăn / tóc', feet: 'Giày dép', hand: 'Cầm tay', neck: 'Cổ', jewelry: 'Trang sức' };
export const VIEWS: [string, string][] = [['truoc', 'Trước'], ['phai', 'Phải'], ['sau', 'Sau'], ['trai', 'Trái']];
export const SVGNS = 'http://www.w3.org/2000/svg';

const svgCache: Record<string, string | null> = {};
export async function layer(path: string): Promise<string | null> {
  if (!(path in svgCache)) {
    const r = await fetch(`/figure/${path}.svg`);
    const m = r.ok ? (await r.text()).replace(/<!--[\s\S]*?-->/g, '').match(/<svg[^>]*>([\s\S]*)<\/svg>/) : null;
    svgCache[path] = m ? m[1] : null;
  }
  return svgCache[path];
}
export function layerPaths(s: OutfitState, v: string): string[] {
  const sfx = v === 'truoc' ? '' : `_${v}`;
  const acc = [...s.accessories].sort((a, b) => SLOT_ORDER.indexOf(CAT.acc[a]?.slot) - SLOT_ORDER.indexOf(CAT.acc[b]?.slot));
  return [`body/body_${s.gender}`,
    ['ao_tu_than', 'nhat_binh'].includes(s.garment) ? 'bottom/vay_nu' : `bottom/quan_${s.gender}`,
    `garment/${s.garment}_${s.gender}`, ...acc.map(a => `accessory/${a}${CAT.acc[a]?.byGender ? '_' + s.gender : ''}`)].map(p => p + sfx);
}
export function patternDef(patId: string, baseHex: string, id: string): string | null {
  const p = CAT.pattern[patId];
  if (!p || !p.tile) return null;
  return `<pattern id="${id}" patternUnits="userSpaceOnUse" width="${p.tile}" height="${p.tile}">` +
         `<rect width="${p.tile}" height="${p.tile}" fill="${baseHex}"/>${p.motif.replace(/'/g, '"')}</pattern>`;
}

const MOTIF_SPAN = 62;
const motifCache: Record<string, { top: string; bottom: string }> = {};
const boxCache: Record<string, DOMRect> = {};
const MOTIF_LIGHT = '#F3EDE4', MOTIF_ON_LIGHT = '#7A6E62';
const lightBase = (h: string) => { const n = parseInt(h.slice(1), 16); return (0.299 * (n >> 16) + 0.587 * (n >> 8 & 255) + 0.114 * (n & 255)) / 255 > 0.72; };
let figSeq = 0;
export async function motif(id: string) {
  if (!(id in motifCache)) {
    const r = await fetch(`/figure/motif/${id}.svg`);
    const doc = new DOMParser().parseFromString(r.ok ? await r.text() : '<svg/>', 'image/svg+xml');
    const part = (a: string) => doc.querySelector(`[data-anchor="${a}"]`)?.innerHTML || '';
    motifCache[id] = { top: part('top'), bottom: part('bottom') };
  }
  return motifCache[id];
}
export const motifTop = (id: string) => motifCache[id]?.top || '';
const isSleeve = (el: Element) => { for (let e: Element | null = el; e && e.tagName !== 'svg'; e = e.parentElement) if ((e.id || '').startsWith('tay')) return true; return false; };
function torsoBox(key: string, mains: Element[]): DOMRect {
  if (!boxCache[key]) {
    const tmp = document.createElementNS(SVGNS, 'svg');
    tmp.setAttribute('style', 'position:absolute;left:-9999px;width:400px;height:800px');
    tmp.innerHTML = mains.map(m => m.outerHTML).join('');
    document.body.appendChild(tmp); boxCache[key] = tmp.getBBox(); tmp.remove();
  }
  return boxCache[key];
}
async function withPlacement(markup: string, key: string, patId: string, v: string): Promise<string> {
  const doc = new DOMParser().parseFromString(`<svg xmlns="${SVGNS}">${markup}</svg>`, 'image/svg+xml');
  const mains = [...doc.querySelectorAll('[fill="#FF0000"]')].filter(e => !isSleeve(e));
  if (!mains.length) return markup;
  const box = torsoBox(key, mains), m = await motif(patId), k = box.width / MOTIF_SPAN, cid = `clip${++figSeq}`;
  const cx = box.x + box.width / 2, flip = v === 'sau';
  const short = box.height < 3 * box.width ? 0.6 : 1;
  const tf = (y: number, z = 1) => flip ? `translate(${cx + 50 * k * z} ${y}) scale(${-k * z} ${k * z})` : `translate(${cx - 50 * k * z} ${y}) scale(${k * z})`;
  const g = doc.createElementNS(SVGNS, 'g');
  g.setAttribute('id', 'hoa_tiet_dat');
  g.innerHTML = `<clipPath id="${cid}">${mains.map(e => { const c = e.cloneNode() as Element; c.removeAttribute('id'); return c.outerHTML; }).join('')}</clipPath>
    <g clip-path="url(#${cid})" stroke="none" stroke-opacity="1" stroke-width="1" stroke-linejoin="round"><g transform="${tf(box.y)}">${m.top}</g><g transform="${tf(box.y + box.height, short)}">${m.bottom}</g></g>`;
  const last = mains[mains.length - 1];
  last.parentNode!.insertBefore(g, last.nextSibling);
  return doc.documentElement.innerHTML;
}
export async function figureSVG(s: OutfitState, v = 'truoc'): Promise<{ svg: string; missing: string[] }> {
  const hex = (id?: string | null) => (id && CAT.color[id]?.hex) || '#cccccc';
  const pid = `pat${++figSeq}`;
  const pdef = CAT.pattern[s.pattern || 'tron'];
  const place = pdef?.kind === 'placement' && (!pdef.garments || pdef.garments.includes(s.garment)) && (!pdef.genders || pdef.genders.includes(s.gender));
  const pat = place ? null : patternDef(s.pattern || 'tron', hex(s.colors.main), pid);
  const map: Record<string, string> = { '#FF0000': pat ? `url(#${pid})` : hex(s.colors.main), '#00FF00': hex(s.colors.lining || 'trang_nga'),
                '#0000FF': hex(s.colors.bottom), '#FF00FF': hex(s.colors.accent || s.colors.main) };
  let inner = '';
  const missing: string[] = [];
  for (const p of layerPaths(s, v)) {
    let body = await layer(p);
    if (body === null) { missing.push(p); continue; }
    if (place && p.startsWith('garment/')) body = await withPlacement(body, p, s.pattern!, v);
    if (place && lightBase(hex(s.colors.main))) body = body.replaceAll(MOTIF_LIGHT, MOTIF_ON_LIGHT);
    inner += body.replace(/#(FF0000|00FF00|0000FF|FF00FF)/gi, m => map[m.toUpperCase()]);
  }
  return { svg: `<svg viewBox="0 0 400 800" xmlns="${SVGNS}">${pat ? `<defs>${pat}</defs>` : ''}${inner}</svg>`, missing };
}
export const patternOk = (p: { garments?: string[]; genders?: string[] }, s: OutfitState) =>
  (!p.garments || p.garments.includes(s.garment)) && (!p.genders || p.genders.includes(s.gender));
