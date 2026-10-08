// Checklist "soi và mặc theo" + thẻ Lookbook 1080×1350 (vẽ ngay trên trình duyệt, không gọi AI, không tải gì lên máy chủ).
import { catalog, figureSVG, layer, layerPaths, SLOT_NAME, SLOT_ORDER, SVGNS } from './figure';
import type { OutfitState, ScoreCard } from './types';

export interface CkItem { group: string; name: string; color: { name: string; hex: string } | null; tip: string }
export interface Note { title: string; comment: string; tip: string; card: ScoreCard | null | undefined }

const colorInfo = (id: string) => { const c = catalog().color[id]; return { name: c?.name || id, hex: (c?.hex || '#cccccc').toUpperCase() }; };
export const noMark = (t: string) => t.normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/đ/g, 'd').replace(/Đ/g, 'D');
const SKIRT = ['ao_tu_than', 'nhat_binh'];

export async function outfitItems(s: OutfitState): Promise<CkItem[]> {
  const CAT = catalog(), C = CAT.checklist || {}, items: CkItem[] = [], g = CAT.garment[s.garment];
  const pat = s.pattern && s.pattern !== 'tron' ? CAT.pattern[s.pattern]?.name : '';
  items.push({ group: 'Áo', name: `${g.name} ${s.gender === 'nu' ? 'nữ' : 'nam'}${pat ? ', hoạ tiết ' + pat : ''}`, color: colorInfo(s.colors.main), tip: C.garments?.[s.garment] || '' });
  const body = await layer(`garment/${s.garment}_${s.gender}`);
  if (body && /#00FF00/i.test(body)) items.push({ group: 'Lót / viền', name: C.lining || 'Viền, lót', color: colorInfo(s.colors.lining || 'trang_nga'), tip: '' });
  const skirt = SKIRT.includes(s.garment);
  items.push({ group: skirt ? 'Váy' : 'Quần', name: skirt ? 'Váy dài' : 'Quần ống suông', color: colorInfo(s.colors.bottom), tip: C.bottoms?.[skirt ? 'vay' : 'quan'] || '' });
  const acc = [...s.accessories].sort((a, b) => SLOT_ORDER.indexOf(CAT.acc[b]?.slot) - SLOT_ORDER.indexOf(CAT.acc[a]?.slot));
  for (const a of acc) {
    const info = CAT.acc[a];
    items.push({ group: SLOT_NAME[info?.slot] || 'Phụ kiện', name: info?.name || a, color: info?.usesAccent ? colorInfo(s.colors.accent || s.colors.main) : null, tip: C.accessories?.[a] || '' });
  }
  return items;
}
export function cultureLine(garmentId: string) {
  const c = catalog().cultureCards.find(x => x.garmentId === garmentId);
  if (!c) return null;
  const first = (c.body.match(/^[^.!?]+[.!?]/) || [c.body])[0].trim();
  return { text: first, verified: !!c.verified };
}
export function checklistText(items: CkItem[], note: Note): string {
  const lines = ['Nếp Áo – Checklist bản phối', ...items.map(it => `☐ ${it.group}: ${it.name}${it.color ? ` – ${it.color.name} (${it.color.hex})` : ''}${it.tip ? `\n   ${it.tip}` : ''}`)];
  if (note.card) lines.push(`Điểm: ${note.card.total}/100 · ${note.card.bandText}`);
  if (note.tip) lines.push(`Mẹo stylist: ${note.tip}`);
  return lines.join('\n');
}

/* ---------------- vẽ canvas ---------------- */
function wrapText(ctx: CanvasRenderingContext2D, text: string, maxW: number): string[] {
  const words = String(text || '').split(/\s+/), lines: string[] = [];
  let cur = '';
  for (const w of words) {
    const t = cur ? cur + ' ' + w : w;
    if (ctx.measureText(t).width > maxW && cur) { lines.push(cur); cur = w; } else cur = t;
  }
  if (cur) lines.push(cur);
  return lines;
}
function textBlock(ctx: CanvasRenderingContext2D, text: string, x: number, y: number, maxW: number, lh: number, maxLines?: number): number {
  let lines = wrapText(ctx, text, maxW);
  if (maxLines && lines.length > maxLines) { lines = lines.slice(0, maxLines); lines[maxLines - 1] = lines[maxLines - 1].replace(/\s*\S*$/, '').replace(/[\s.,;:!?…]+$/, '') + '…'; }
  lines.forEach((l, i) => ctx.fillText(l, x, y + i * lh));
  return y + lines.length * lh;
}
async function svgImage(svg: string): Promise<HTMLImageElement> {
  const src = svg.replace('<svg ', '<svg width="800" height="1600" ');
  const url = URL.createObjectURL(new Blob([src], { type: 'image/svg+xml' }));
  const img = new Image(); img.src = url;
  try { await img.decode(); } finally { URL.revokeObjectURL(url); }
  return img;
}
const SERIF = '"Playfair Display", Georgia, serif', SANS = '"Be Vietnam Pro", system-ui, sans-serif';
async function layerBox(markup: string): Promise<DOMRect | null> {
  const tmp = document.createElementNS(SVGNS, 'svg');
  tmp.setAttribute('style', 'position:absolute;left:-9999px;width:400px;height:800px');
  tmp.innerHTML = markup;
  document.body.appendChild(tmp);
  try { const b = tmp.getBBox(); return b.width ? b : null; } finally { tmp.remove(); }
}
async function itemAnchors(s: OutfitState) {
  const out: { path: string; x: number; y: number }[] = [];
  for (const p of layerPaths(s, 'truoc').slice(1)) {
    const body = await layer(p);
    if (!body) continue;
    const b = await layerBox(body);
    if (!b) continue;
    let ax = b.x + b.width / 2, ay = b.y + b.height / 2;
    if (p.startsWith('garment/')) { ax = b.x + b.width * 0.62; ay = b.y + b.height * 0.22; }
    else if (p.startsWith('bottom/')) { ax = b.x + b.width * 0.66; ay = b.y + b.height * 0.78; }
    else if (/accessory\/(guoc|hai_theu|giay|sneaker)/.test(p)) { ax = b.x + b.width * 0.8; }
    else if (/accessory\/non/.test(p)) { ax = b.x + b.width * 0.82; ay = b.y + Math.min(b.height * 0.5, 34); }
    else if (/accessory\/(khan|hoa|kieng|trang_suc)/.test(p)) { ax = b.x + b.width * 0.9; ay = b.y + b.height * 0.55; }
    out.push({ path: p, x: ax, y: ay });
  }
  return out;
}
function hexA(hex: string, a: number) { const n = parseInt(hex.slice(1), 16); return `rgba(${n >> 16},${n >> 8 & 255},${n & 255},${a})`; }
function seeded(seed: number) { return () => { seed |= 0; seed = seed + 0x6D2B79F5 | 0; let t = Math.imul(seed ^ seed >>> 15, 1 | seed); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }

/* Nền thẻ: giấy điệp (vệt chổi lá thông + hạt điệp) và khung vòm lấy cảm hứng cửa võng (viền kép, hồi văn ở chân, cuộn mây ở hai góc). */
function drawBackdrop(ctx: CanvasRenderingContext2D, W: number, H: number, tint: string, red: string, floorY: number) {
  const rnd = seeded(20261008);
  const bg = ctx.createLinearGradient(0, 0, 0, H);
  bg.addColorStop(0, '#f6efe2'); bg.addColorStop(1, '#efe4d0');
  ctx.fillStyle = bg; ctx.fillRect(0, 0, W, H);
  for (let i = 0; i < 170; i++) {
    const y = rnd() * H, dy = (rnd() - 0.5) * 40;
    ctx.strokeStyle = `rgba(150,118,80,${0.025 + rnd() * 0.05})`; ctx.lineWidth = 0.6 + rnd() * 2.2;
    ctx.beginPath(); ctx.moveTo(-20, y); ctx.bezierCurveTo(W * 0.3, y + dy * 0.4, W * 0.7, y - dy * 0.3, W + 20, y + dy); ctx.stroke();
  }
  for (let i = 0; i < 1400; i++) {
    const x = rnd() * W, y = rnd() * H, r = 0.4 + rnd() * 1.3;
    ctx.fillStyle = rnd() < 0.82 ? `rgba(255,255,255,${0.35 + rnd() * 0.45})` : `rgba(140,110,70,${0.08 + rnd() * 0.12})`;
    ctx.beginPath(); ctx.arc(x, y, r, 0, Math.PI * 2); ctx.fill();
  }
  const X0 = 86, X1 = 554, CX = (X0 + X1) / 2, R = (X1 - X0) / 2, TOP = 236 + R, BOT = floorY + 6;
  const arch = (inset: number) => { ctx.beginPath(); ctx.moveTo(X0 + inset, BOT); ctx.lineTo(X0 + inset, TOP); ctx.arc(CX, TOP, R - inset, Math.PI, 0); ctx.lineTo(X1 - inset, BOT); };
  arch(0); ctx.closePath();
  const inner = ctx.createLinearGradient(0, 262, 0, BOT);
  inner.addColorStop(0, hexA(tint, 0.10)); inner.addColorStop(1, hexA(tint, 0.22));
  ctx.fillStyle = inner; ctx.fill();
  ctx.strokeStyle = hexA(red, 0.55); ctx.lineWidth = 3; arch(-8); ctx.stroke();
  ctx.strokeStyle = hexA(red, 0.35); ctx.lineWidth = 1.2; arch(4); ctx.stroke();
  const cloud = (x: number, y: number, dir: number) => {
    ctx.save(); ctx.translate(x, y); ctx.scale(dir, 1);
    ctx.strokeStyle = hexA(red, 0.5); ctx.lineWidth = 2; ctx.beginPath();
    ctx.arc(0, 0, 14, Math.PI * 0.5, Math.PI * 2.2); ctx.arc(10, -4, 6, Math.PI * 1.2, Math.PI * 2.6);
    ctx.moveTo(-14, 6); ctx.quadraticCurveTo(-30, 18, -12, 26); ctx.arc(-4, 22, 8, Math.PI, Math.PI * 2.4);
    ctx.stroke(); ctx.restore();
  };
  cloud(X0 + 26, TOP + 4, 1); cloud(X1 - 26, TOP + 4, -1);
  ctx.strokeStyle = hexA(red, 0.45); ctx.lineWidth = 1.6;
  const U = 18, y0 = BOT + 6;
  ctx.beginPath();
  for (let x = X0 - 8; x + U <= X1 + 8; x += U) {
    ctx.moveTo(x, y0 + U); ctx.lineTo(x, y0); ctx.lineTo(x + U * 0.78, y0); ctx.lineTo(x + U * 0.78, y0 + U * 0.6);
    ctx.lineTo(x + U * 0.34, y0 + U * 0.6); ctx.lineTo(x + U * 0.34, y0 + U * 0.3);
  }
  ctx.stroke();
  ctx.strokeStyle = hexA(red, 0.55); ctx.lineWidth = 3;
  ctx.beginPath(); ctx.moveTo(X0 - 8, BOT); ctx.lineTo(X1 + 8, BOT); ctx.moveTo(X0 - 8, y0 + U + 6); ctx.lineTo(X1 + 8, y0 + U + 6); ctx.stroke();
  const sh = ctx.createRadialGradient(CX, BOT - 6, 4, CX, BOT - 6, 170);
  sh.addColorStop(0, 'rgba(60,40,20,0.22)'); sh.addColorStop(1, 'rgba(60,40,20,0)');
  ctx.save(); ctx.scale(1, 0.12); ctx.fillStyle = sh; ctx.beginPath(); ctx.arc(CX, (BOT - 6) / 0.12, 170, 0, Math.PI * 2); ctx.fill(); ctx.restore();
}

export async function drawLookbook(s: OutfitState, note: Note): Promise<HTMLCanvasElement> {
  const CAT = catalog();
  await Promise.all([`italic 700 60px ${SERIF}`, `900 120px ${SERIF}`, `400 24px ${SANS}`, `600 24px ${SANS}`, `italic 400 28px ${SERIF}`].map(f => document.fonts.load(f, 'Nếp Áo Việt phục')));
  const W = 1080, H = 1350, cv = document.createElement('canvas'); cv.width = W; cv.height = H;
  const ctx = cv.getContext('2d')!, g = CAT.garment[s.garment];
  const items = await outfitItems(s), main = colorInfo(s.colors.main);
  const INK = '#231f1a', MUTED = '#7a6f62', RED = '#9b2c1f', PAPER = '#f7f1e7';
  const serif = (sz: number, w = 700, it = '') => `${it} ${w} ${sz}px ${SERIF}`, sans = (sz: number, w = 400) => `${w} ${sz}px ${SANS}`;
  const FX = 50, FY = 176, FW = 540, FH = 1080;
  drawBackdrop(ctx, W, H, main.hex, RED, FY + 781 / 800 * FH);
  ctx.fillStyle = INK; ctx.font = serif(118, 900); ctx.textBaseline = 'alphabetic';
  ctx.fillText('NẾP ÁO', 56, 148);
  const mw = ctx.measureText('NẾP ÁO').width;
  ctx.font = sans(19, 600); ctx.fillStyle = RED; ctx.fillText('VIỆT PHỤC REMIX', 56 + mw + 28, 104);
  ctx.fillStyle = MUTED; ctx.font = sans(19);
  const now = new Date();
  ctx.fillText(`Lookbook · Tháng ${now.getMonth() + 1}/${now.getFullYear()}`, 56 + mw + 28, 134);
  ctx.fillStyle = INK; ctx.fillRect(56, 172, W - 112, 2); ctx.fillRect(56, 178, W - 112, 1);
  const img = await svgImage((await figureSVG(s, 'truoc')).svg);
  ctx.drawImage(img, FX, FY, FW, FH);
  const toC = (x: number, y: number) => [FX + x / 400 * FW, FY + y / 800 * FH];
  const RX = 640, RW = W - RX - 56;
  let y = 262;
  ctx.fillStyle = INK; ctx.font = serif(54, 700, 'italic');
  const occ = CAT.occasion[s.occasion]?.name;
  y = textBlock(ctx, note.title || g.name, RX, y, RW, 62, 3);
  ctx.fillStyle = MUTED; ctx.font = sans(21);
  y = textBlock(ctx, `${g.name} ${s.gender === 'nu' ? 'nữ' : 'nam'} · ${CAT.style[s.style]?.name || ''}${occ ? ' · ' + occ : ''}`, RX, y + 6, RW, 28, 2) + 22;
  const anchors = await itemAnchors(s);
  const key = (it: CkItem) => it.group === 'Áo' ? 'garment/' : (it.group === 'Váy' || it.group === 'Quần') ? 'bottom/' : null;
  const accOrder = anchors.filter(a => a.path.startsWith('accessory/'));
  const accSorted = [...s.accessories].sort((a, b) => SLOT_ORDER.indexOf(CAT.acc[b]?.slot) - SLOT_ORDER.indexOf(CAT.acc[a]?.slot));
  let ai = 0;
  const shown = items.filter(it => it.group !== 'Lót / viền').map(it => {
    const k = key(it) || `accessory/${accSorted[ai++]}`;
    const a = (k.startsWith('accessory/') ? accOrder : anchors).find(an => an.path.startsWith(k));
    return { ...it, a };
  }).sort((p, q) => (p.a ? p.a.y : 999) - (q.a ? q.a.y : 999)).slice(0, 6);
  shown.forEach((it, i) => {
    const rowY = y;
    ctx.fillStyle = RED; ctx.font = serif(30, 700, 'italic'); ctx.fillText(String(i + 1).padStart(2, '0'), RX, rowY + 26);
    ctx.fillStyle = INK; ctx.font = sans(23, 600);
    let yy = textBlock(ctx, it.name, RX + 52, rowY + 24, RW - 52, 29, 2);
    if (it.color) {
      ctx.fillStyle = it.color.hex; ctx.beginPath(); ctx.arc(RX + 61, yy + 4, 9, 0, Math.PI * 2); ctx.fill();
      ctx.strokeStyle = 'rgba(0,0,0,.2)'; ctx.lineWidth = 1.5; ctx.stroke();
      ctx.fillStyle = MUTED; ctx.font = sans(18); ctx.fillText(`${it.color.name}  ${it.color.hex}`, RX + 78, yy + 10);
      yy += 26;
    }
    const a = it.a;
    if (a) {
      const [px, py] = toC(a.x, a.y), ty = rowY + 17;
      ctx.strokeStyle = hexA('#231f1a', 0.55); ctx.lineWidth = 1.4;
      ctx.beginPath(); ctx.moveTo(px, py); ctx.lineTo(RX - 46, ty); ctx.lineTo(RX - 10, ty); ctx.stroke();
      ctx.fillStyle = PAPER; ctx.beginPath(); ctx.arc(px, py, 7, 0, Math.PI * 2); ctx.fill();
      ctx.strokeStyle = RED; ctx.lineWidth = 2.5; ctx.stroke();
    }
    y = yy + 18;
  });
  if (note.comment && y < 1060) {
    y += 14;
    ctx.fillStyle = hexA(RED, 0.85); ctx.font = serif(90, 700); ctx.fillText('“', RX - 6, y + 52);
    ctx.fillStyle = INK; ctx.font = serif(25, 400, 'italic');
    y = textBlock(ctx, note.comment, RX + 36, y + 30, RW - 36, 34, Math.max(2, Math.floor((1110 - y) / 34)));
    ctx.fillStyle = MUTED; ctx.font = sans(17, 600); ctx.fillText('— STYLIST NẾP ÁO', RX + 36, y + 8);
  }
  if (note.card) {
    ctx.save(); ctx.translate(948, 100); ctx.rotate(-0.12);
    ctx.strokeStyle = RED; ctx.lineWidth = 4; ctx.beginPath(); ctx.arc(0, 0, 68, 0, Math.PI * 2); ctx.stroke();
    ctx.lineWidth = 1.5; ctx.beginPath(); ctx.arc(0, 0, 61, 0, Math.PI * 2); ctx.stroke();
    ctx.fillStyle = PAPER; ctx.beginPath(); ctx.arc(0, 0, 60, 0, Math.PI * 2); ctx.fill();
    ctx.fillStyle = RED; ctx.textAlign = 'center';
    ctx.font = serif(52, 900); ctx.fillText(String(note.card.total), 0, 14);
    ctx.font = sans(14, 700); ctx.fillText(note.card.bandText.toUpperCase(), 0, 40);
    ctx.font = sans(11, 600); ctx.fillText('ĐIỂM / 100', 0, -32);
    ctx.restore(); ctx.textAlign = 'left';
  }
  const sw: [string, string][] = [['Áo', s.colors.main], [SKIRT.includes(s.garment) ? 'Váy' : 'Quần', s.colors.bottom]];
  if (items.some(it => it.group === 'Lót / viền')) sw.push(['Viền', s.colors.lining || 'trang_nga']);
  if (s.accessories.some(a => CAT.acc[a]?.usesAccent)) sw.push(['Điểm nhấn', s.colors.accent || s.colors.main]);
  const PX = 640, PY = 1170, PW = (W - 56 - PX) / sw.length;
  sw.forEach(([lab, id], i) => {
    const c = colorInfo(id), x0 = PX + i * PW;
    ctx.fillStyle = c.hex; ctx.fillRect(x0, PY, PW - 8, 54);
    ctx.strokeStyle = 'rgba(0,0,0,.12)'; ctx.lineWidth = 1; ctx.strokeRect(x0, PY, PW - 8, 54);
    ctx.fillStyle = INK; ctx.font = sans(15, 600); ctx.fillText(lab.toUpperCase(), x0, PY + 76);
    ctx.fillStyle = MUTED; ctx.font = sans(14); ctx.fillText(c.hex, x0, PY + 96);
  });
  const cul = cultureLine(s.garment);
  ctx.fillStyle = INK; ctx.fillRect(56, 1290, W - 112, 1);
  if (cul) { ctx.fillStyle = MUTED; ctx.font = serif(17, 400, 'italic'); textBlock(ctx, cul.text, 56, 1314, W - 112, 22, 1); }
  ctx.fillStyle = RED; ctx.font = sans(15, 600);
  ctx.fillText(['#VietPhuc', '#NepAo', '#VietPhucRemix', '#' + noMark(g.name).replace(/\s+/g, '')].join('  '), 56, 1336);
  if (cul && !cul.verified) { ctx.fillStyle = MUTED; ctx.font = sans(13); ctx.textAlign = 'right'; ctx.fillText('Thông tin văn hoá đang được kiểm chứng nguồn', W - 56, 1336); ctx.textAlign = 'left'; }
  return cv;
}

export async function drawChecklist(s: OutfitState, note: Note): Promise<HTMLCanvasElement> {
  const CAT = catalog();
  await document.fonts.ready;
  const W = 1080, H = 1350, cv = document.createElement('canvas'); cv.width = W; cv.height = H;
  const ctx = cv.getContext('2d')!;
  const F = (size: number, weight = 400) => `${weight} ${size}px ${SANS}`;
  const items = await outfitItems(s), g = CAT.garment[s.garment];
  ctx.fillStyle = '#faf6ef'; ctx.fillRect(0, 0, W, H);
  ctx.strokeStyle = '#8b2e1f'; ctx.lineWidth = 3; ctx.strokeRect(28, 28, W - 56, H - 56);
  ctx.fillStyle = '#8b2e1f'; ctx.font = F(30, 700); ctx.fillText('NẾP ÁO', 64, 92);
  ctx.fillStyle = '#6b645a'; ctx.font = F(24); ctx.fillText('Checklist soi và mặc theo', 200, 92);
  ctx.fillStyle = '#e6ddcc'; ctx.fillRect(64, 112, W - 128, 2);
  const img = await svgImage((await figureSVG(s, 'truoc')).svg);
  ctx.drawImage(img, 40, 130, 520, 1040);
  const x = 580, colW = W - x - 64;
  let y = 190;
  ctx.fillStyle = '#2b2b2b'; ctx.font = F(48, 700);
  const occ = CAT.occasion[s.occasion]?.name;
  y = textBlock(ctx, note.title || `${g.name}${occ ? ' · ' + occ : ''}`, x, y, colW, 58, 2) + 6;
  ctx.fillStyle = '#6b645a'; ctx.font = F(26);
  y = textBlock(ctx, `${g.name} ${s.gender === 'nu' ? 'nữ' : 'nam'} · ${CAT.style[s.style]?.name || ''}`, x, y + 8, colW, 34, 2) + 18;
  for (const it of items) {
    if (y > 1080) break;
    ctx.strokeStyle = '#2b2b2b'; ctx.lineWidth = 2; ctx.strokeRect(x, y + 4, 26, 26);
    ctx.fillStyle = '#6b645a'; ctx.font = F(22, 600); ctx.fillText(it.group.toUpperCase(), x + 42, y + 10);
    ctx.fillStyle = '#2b2b2b'; ctx.font = F(27, 600);
    let yy = textBlock(ctx, it.name, x + 42, y + 42, colW - 42, 34, 2);
    if (it.color) {
      ctx.fillStyle = it.color.hex; ctx.beginPath(); ctx.arc(x + 54, yy + 6, 12, 0, Math.PI * 2); ctx.fill();
      ctx.strokeStyle = 'rgba(0,0,0,.25)'; ctx.stroke();
      ctx.fillStyle = '#2b2b2b'; ctx.font = F(23); ctx.fillText(`${it.color.name} · ${it.color.hex}`, x + 74, yy + 14); yy += 32;
    }
    if (it.tip) { ctx.fillStyle = '#6b645a'; ctx.font = F(21); yy = textBlock(ctx, it.tip, x + 42, yy + 16, colW - 42, 27, 2); }
    y = yy + 22;
  }
  if (note.card && y < 1120) { ctx.fillStyle = '#8b2e1f'; ctx.font = F(28, 700); ctx.fillText(`${note.card.total}/100 · ${note.card.bandText}`, x, y + 20); }
  const cul = cultureLine(s.garment);
  ctx.fillStyle = '#f1e9da'; ctx.fillRect(40, 1180, W - 80, 104);
  ctx.fillStyle = '#2b2b2b'; ctx.font = F(23);
  if (cul) textBlock(ctx, cul.text, 64, 1218, W - 128, 30, 2);
  ctx.fillStyle = '#6b645a'; ctx.font = F(19);
  ctx.fillText(['#VietPhuc', '#NepAo', '#VietPhucRemix', '#' + noMark(g.name).replace(/\s+/g, '')].join('  ') + (cul && !cul.verified ? '   · Thông tin văn hoá đang được kiểm chứng nguồn' : ''), 64, 1312);
  return cv;
}
export function downloadCanvas(cv: HTMLCanvasElement, name: string) {
  cv.toBlob(b => { if (!b) return; const a = document.createElement('a'); a.href = URL.createObjectURL(b); a.download = name; a.click(); setTimeout(() => URL.revokeObjectURL(a.href), 2000); }, 'image/png');
}
