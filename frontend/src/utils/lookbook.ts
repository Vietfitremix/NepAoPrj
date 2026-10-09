// Checklist "soi và mặc theo" + thẻ Lookbook 1080×1350, vẽ ngay trên trình duyệt (không tải gì lên máy chủ).
// Người mẫu lấy từ tủ đồ PNG của vietfit (paintWardrobe); phần chữ, bảng màu, con dấu điểm và nền giấy điệp là của AI Nếp Áo.
import { paintWardrobe } from '../components/mix/WardrobeFigure';
import { accessorySlots, getWardrobe, selectedWardrobeItems } from './maleWardrobe';
import type { MaleSelection, WardrobeCharacter, WardrobeItem } from './maleWardrobe';
import { characterHeadroom } from './renderMaleCharacter';
import { wardrobeColors } from './wardrobeStyles';

export interface ScoreCriterion { id: string; name: string; weight: number; score: number; ruleIds: string[]; notes: string[] }
export interface ScoreCardData { total: number; band: 'chuan_bo' | 'hop_dip' | 'can_chinh'; bandText: string; capped?: boolean; criteria: ScoreCriterion[] }
export interface ReviewNote { title: string; comment: string; tip: string; card?: ScoreCardData | null }
export interface CkItem { group: string; name: string; detail: string; color: { name: string; hex: string } | null; tip: string; anchor: [number, number] }
export interface ChecklistTips { garments?: Record<string, string>; bottoms?: Record<string, string>; accessories?: Record<string, string>; lining?: string }
export interface CultureCardData { garmentId: string; title: string; body: string; verified?: boolean }
export interface LookbookExtras { tips: ChecklistTips; cultureCards: CultureCardData[]; styleName: string; eventName: string }

const SHIRT_TO_GARMENT: Record<string, string> = { navy: 'ao_dai', burgundy: 'ao_dai', teal: 'ao_dai', jade: 'ao_dai', rose: 'ao_dai',
  'tu-than': 'ao_tu_than', 'ngu-than': 'ao_ngu_than', 'nhat-binh': 'nhat_binh', 'ba-ba': 'ao_ba_ba' };
const TIP_ID: Record<string, string> = { 'tui-coi': 'tui', 'quat-giay': 'quat_giay', 'bong-tai': 'trang_suc', 'vong-tay': 'trang_suc' };
// Vị trí tương đối (x, y) của từng món trên canvas người mẫu, để kẻ đường chú thích từ món tới số thứ tự.
const ANCHOR: Record<string, [number, number]> = { shirt: [0.6, 0.36], pants: [0.58, 0.68], shoes: [0.58, 0.93], headwear: [0.6, 0.12],
  headphones: [0.62, 0.15], glasses: [0.56, 0.17], hairAccessory: [0.6, 0.15], necklace: [0.54, 0.24], earrings: [0.6, 0.19],
  bracelet: [0.73, 0.5], gloves: [0.74, 0.54], hipChain: [0.6, 0.5], backpack: [0.32, 0.4], bag: [0.7, 0.55], bagCharm: [0.7, 0.6], fan: [0.72, 0.52] };
const SKIRT = /váy/i;
const colorLabel = (hex: string) => { const f = wardrobeColors.find(c => c.value.toLowerCase() === hex.toLowerCase()); return f?.name || 'Màu tự chọn'; };
export const noMark = (t: string) => t.normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/đ/g, 'd').replace(/Đ/g, 'D');

export function checklistItems(selection: MaleSelection, character: WardrobeCharacter, tips: ChecklistTips): CkItem[] {
  const items: CkItem[] = [];
  const garment = SHIRT_TO_GARMENT[selection.shirt || ''];
  const custom = (slot: 'shirt' | 'pants' | 'shoes') => { const c = selection.styles?.[slot]?.color; return c ? { name: colorLabel(c), hex: c.toUpperCase() } : null; };
  for (const it of selectedWardrobeItems(selection, character) as WardrobeItem[]) {
    const isShirt = it.id === selection.shirt, isPants = it.id === selection.pants && !isShirt;
    const isShoe = !isShirt && !isPants && getWardrobe(character).shoes.some(s => s.id === it.id) && it.id === selection.shoes;
    if (isShirt) items.push({ group: 'Áo', name: custom('shirt') ? it.name.replace(/\s+(xanh ngọc|xanh navy|xanh|hồng|đỏ)$/i, '') : it.name, detail: it.detail, color: custom('shirt'), tip: tips.garments?.[garment] || '', anchor: ANCHOR.shirt });
    else if (isPants) items.push({ group: SKIRT.test(it.name) ? 'Váy' : 'Quần', name: it.name, detail: it.detail, color: custom('pants'),
      tip: tips.bottoms?.[SKIRT.test(it.name) ? 'vay' : 'quan'] || '', anchor: ANCHOR.pants });
    else if (isShoe) items.push({ group: 'Giày dép', name: it.name, detail: it.detail, color: custom('shoes'), tip: '', anchor: ANCHOR.shoes });
    else items.push({ group: accessorySlots.find(s => s.id === it.slot)?.name || 'Phụ kiện', name: it.name, detail: it.detail, color: null,
      tip: tips.accessories?.[TIP_ID[it.id] || it.id.replace(/-/g, '_')] || '', anchor: ANCHOR[it.slot || ''] || [0.6, 0.5] });
  }
  return items;
}
export function cultureLine(selection: MaleSelection, cards: CultureCardData[]) {
  const c = cards.find(x => x.garmentId === SHIRT_TO_GARMENT[selection.shirt || '']);
  if (!c) return null;
  return { text: (c.body.match(/^[^.!?]+[.!?]/) || [c.body])[0].trim(), verified: !!c.verified };
}
export function checklistText(items: CkItem[], note: ReviewNote): string {
  const lines = ['Nếp Áo – Checklist bản phối', ...items.map(it => `☐ ${it.group}: ${it.name}${it.color ? ` – ${it.color.name} (${it.color.hex})` : ''}${it.tip ? `\n   ${it.tip}` : ''}`)];
  if (note.card) lines.push(`Điểm: ${note.card.total}/100 · ${note.card.bandText}`);
  if (note.tip) lines.push(`Recommend: ${note.tip}`);
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
const SERIF = '"Playfair Display", Georgia, serif', SANS = '"Be Vietnam Pro", system-ui, sans-serif';
const hexA = (hex: string, a: number) => { const n = parseInt(hex.slice(1), 16); return `rgba(${n >> 16},${n >> 8 & 255},${n & 255},${a})`; };
function seeded(seed: number) { return () => { seed |= 0; seed = seed + 0x6D2B79F5 | 0; let t = Math.imul(seed ^ seed >>> 15, 1 | seed); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }

/* Nền thẻ: giấy điệp (vệt chổi lá thông + hạt điệp) và khung vòm lấy cảm hứng cửa võng (viền kép, hồi văn ở chân, cuộn mây ở hai góc). */
function drawBackdrop(ctx: CanvasRenderingContext2D, W: number, H: number, tint: string, red: string, x0: number, x1: number, top: number, floorY: number) {
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
  const CX = (x0 + x1) / 2, R = (x1 - x0) / 2, TOP = top + R, BOT = floorY + 6;
  const arch = (inset: number) => { ctx.beginPath(); ctx.moveTo(x0 + inset, BOT); ctx.lineTo(x0 + inset, TOP); ctx.arc(CX, TOP, R - inset, Math.PI, 0); ctx.lineTo(x1 - inset, BOT); };
  arch(0); ctx.closePath();
  const inner = ctx.createLinearGradient(0, top, 0, BOT);
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
  cloud(x0 + 26, TOP + 4, 1); cloud(x1 - 26, TOP + 4, -1);
  ctx.strokeStyle = hexA(red, 0.45); ctx.lineWidth = 1.6;
  const U = 18, y0 = BOT + 6;
  ctx.beginPath();
  for (let x = x0 - 8; x + U <= x1 + 8; x += U) {
    ctx.moveTo(x, y0 + U); ctx.lineTo(x, y0); ctx.lineTo(x + U * 0.78, y0); ctx.lineTo(x + U * 0.78, y0 + U * 0.6);
    ctx.lineTo(x + U * 0.34, y0 + U * 0.6); ctx.lineTo(x + U * 0.34, y0 + U * 0.3);
  }
  ctx.stroke();
  ctx.strokeStyle = hexA(red, 0.55); ctx.lineWidth = 3;
  ctx.beginPath(); ctx.moveTo(x0 - 8, BOT); ctx.lineTo(x1 + 8, BOT); ctx.moveTo(x0 - 8, y0 + U + 6); ctx.lineTo(x1 + 8, y0 + U + 6); ctx.stroke();
  const sh = ctx.createRadialGradient(CX, BOT - 6, 4, CX, BOT - 6, 170);
  sh.addColorStop(0, 'rgba(60,40,20,0.22)'); sh.addColorStop(1, 'rgba(60,40,20,0)');
  ctx.save(); ctx.scale(1, 0.12); ctx.fillStyle = sh; ctx.beginPath(); ctx.arc(CX, (BOT - 6) / 0.12, 170, 0, Math.PI * 2); ctx.fill(); ctx.restore();
}

async function figureCanvas(selection: MaleSelection, character: WardrobeCharacter): Promise<HTMLCanvasElement> {
  const w = getWardrobe(character), cv = document.createElement('canvas');
  cv.width = w.width; cv.height = w.height + characterHeadroom;
  await paintWardrobe(cv, selection, character, 'front');
  return cv;
}

export async function drawLookbook(selection: MaleSelection, character: WardrobeCharacter, note: ReviewNote, ex: LookbookExtras): Promise<HTMLCanvasElement> {
  await Promise.all([`italic 700 60px ${SERIF}`, `900 120px ${SERIF}`, `400 24px ${SANS}`, `600 24px ${SANS}`, `italic 400 28px ${SERIF}`].map(f => document.fonts.load(f, 'Nếp Áo Việt phục')));
  const W = 1080, H = 1350, cv = document.createElement('canvas'); cv.width = W; cv.height = H;
  const ctx = cv.getContext('2d')!;
  const items = checklistItems(selection, character, ex.tips);
  const INK = '#231f1a', MUTED = '#7a6f62', RED = '#9b2c1f', PAPER = '#f7f1e7';
  const serif = (sz: number, w = 700, it = '') => `${it} ${w} ${sz}px ${SERIF}`, sans = (sz: number, w = 400) => `${w} ${sz}px ${SANS}`;
  const fig = await figureCanvas(selection, character);
  const FW = 560, FH = Math.round(FW * fig.height / fig.width), FX = 42, FY = 196;
  const tint = selection.styles?.shirt?.color || '#b88a6a';
  drawBackdrop(ctx, W, H, tint, RED, FX + 34, FX + FW - 34, FY + 80, FY + FH * 0.955);
  ctx.fillStyle = INK; ctx.font = serif(118, 900); ctx.textBaseline = 'alphabetic';
  ctx.fillText('NẾP ÁO', 56, 148);
  const mw = ctx.measureText('NẾP ÁO').width;
  ctx.font = sans(19, 600); ctx.fillStyle = RED; ctx.fillText('VIỆT PHỤC REMIX', 56 + mw + 28, 104);
  ctx.fillStyle = MUTED; ctx.font = sans(19);
  const now = new Date();
  ctx.fillText(`Lookbook · Tháng ${now.getMonth() + 1}/${now.getFullYear()}`, 56 + mw + 28, 134);
  ctx.fillStyle = INK; ctx.fillRect(56, 172, W - 112, 2); ctx.fillRect(56, 178, W - 112, 1);
  ctx.drawImage(fig, FX, FY, FW, FH);
  const RX = 660, RW = W - RX - 56;
  let y = 262;
  const garmentName = items[0]?.name || 'Việt phục';
  ctx.fillStyle = INK; ctx.font = serif(54, 700, 'italic');
  y = textBlock(ctx, note.title || garmentName, RX, y, RW, 62, 3);
  ctx.fillStyle = MUTED; ctx.font = sans(21);
  y = textBlock(ctx, `${garmentName} · ${character === 'male' ? 'Nam' : 'Nữ'}${ex.styleName ? ' · ' + ex.styleName : ''}${ex.eventName ? ' · ' + ex.eventName : ''}`, RX, y + 6, RW, 28, 2) + 22;
  const shown = items.slice(0, 6);
  shown.forEach((it, i) => {
    const rowY = y;
    ctx.fillStyle = RED; ctx.font = serif(30, 700, 'italic'); ctx.fillText(String(i + 1).padStart(2, '0'), RX, rowY + 26);
    ctx.fillStyle = INK; ctx.font = sans(23, 600);
    let yy = textBlock(ctx, it.name, RX + 52, rowY + 24, RW - 52, 29, 2);
    ctx.fillStyle = MUTED; ctx.font = sans(17);
    if (it.color) {
      ctx.fillStyle = it.color.hex; ctx.beginPath(); ctx.arc(RX + 61, yy + 4, 9, 0, Math.PI * 2); ctx.fill();
      ctx.strokeStyle = 'rgba(0,0,0,.2)'; ctx.lineWidth = 1.5; ctx.stroke();
      ctx.fillStyle = MUTED; ctx.font = sans(18); ctx.fillText(`${it.color.name}  ${it.color.hex}`, RX + 78, yy + 10);
      yy += 26;
    } else if (it.detail) { ctx.fillText(it.detail, RX + 52, yy + 6); yy += 24; }
    const px = FX + it.anchor[0] * FW, py = FY + it.anchor[1] * FH, ty = rowY + 17;
    ctx.strokeStyle = hexA('#231f1a', 0.5); ctx.lineWidth = 1.3;
    ctx.beginPath(); ctx.moveTo(px, py); ctx.lineTo(RX - 40, ty); ctx.lineTo(RX - 10, ty); ctx.stroke();
    ctx.fillStyle = PAPER; ctx.beginPath(); ctx.arc(px, py, 7, 0, Math.PI * 2); ctx.fill();
    ctx.strokeStyle = RED; ctx.lineWidth = 2.5; ctx.stroke();
    y = yy + 14;
  });
  if (note.comment && y < 1040) {
    y += 14;
    ctx.fillStyle = hexA(RED, 0.85); ctx.font = serif(90, 700); ctx.fillText('“', RX - 6, y + 52);
    ctx.fillStyle = INK; ctx.font = serif(24, 400, 'italic');
    y = textBlock(ctx, note.comment, RX + 36, y + 30, RW - 36, 33, Math.max(2, Math.floor((1090 - y) / 33)));
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
  const sw = items.filter(it => it.color).slice(0, 4);
  const PX = RX, PY = 1176, PW = (W - 56 - PX) / Math.max(sw.length, 1);
  sw.forEach((it, i) => {
    const x0 = PX + i * PW;
    ctx.fillStyle = it.color!.hex; ctx.fillRect(x0, PY, PW - 8, 54);
    ctx.strokeStyle = 'rgba(0,0,0,.12)'; ctx.lineWidth = 1; ctx.strokeRect(x0, PY, PW - 8, 54);
    ctx.fillStyle = INK; ctx.font = sans(15, 600); ctx.fillText(it.group.toUpperCase(), x0, PY + 76);
    ctx.fillStyle = MUTED; ctx.font = sans(14); ctx.fillText(it.color!.hex, x0, PY + 96);
  });
  const cul = cultureLine(selection, ex.cultureCards);
  ctx.fillStyle = INK; ctx.fillRect(56, 1290, W - 112, 1);
  if (cul) { ctx.fillStyle = MUTED; ctx.font = serif(17, 400, 'italic'); textBlock(ctx, cul.text, 56, 1314, W - 112, 22, 1); }
  ctx.fillStyle = RED; ctx.font = sans(15, 600);
  ctx.fillText(['#VietPhuc', '#NepAo', '#VietPhucRemix', '#' + noMark(garmentName).replace(/\s+/g, '')].join('  '), 56, 1336);
  if (cul && !cul.verified) { ctx.fillStyle = MUTED; ctx.font = sans(13); ctx.textAlign = 'right'; ctx.fillText('Thông tin văn hoá đang được kiểm chứng nguồn', W - 56, 1336); ctx.textAlign = 'left'; }
  return cv;
}

export async function drawChecklist(selection: MaleSelection, character: WardrobeCharacter, note: ReviewNote, ex: LookbookExtras): Promise<HTMLCanvasElement> {
  await document.fonts.ready;
  const W = 1080, H = 1350, cv = document.createElement('canvas'); cv.width = W; cv.height = H;
  const ctx = cv.getContext('2d')!;
  const F = (size: number, weight = 400) => `${weight} ${size}px ${SANS}`;
  const items = checklistItems(selection, character, ex.tips);
  ctx.fillStyle = '#faf6ef'; ctx.fillRect(0, 0, W, H);
  ctx.strokeStyle = '#8b2e1f'; ctx.lineWidth = 3; ctx.strokeRect(28, 28, W - 56, H - 56);
  ctx.fillStyle = '#8b2e1f'; ctx.font = F(30, 700); ctx.fillText('NẾP ÁO', 64, 92);
  ctx.fillStyle = '#6b645a'; ctx.font = F(24); ctx.fillText('Checklist soi và mặc theo', 200, 92);
  ctx.fillStyle = '#e6ddcc'; ctx.fillRect(64, 112, W - 128, 2);
  const fig = await figureCanvas(selection, character);
  const FW = 520, FH = Math.round(FW * fig.height / fig.width);
  ctx.drawImage(fig, 40, 150, FW, FH);
  const x = 600, colW = W - x - 64;
  let y = 190;
  ctx.fillStyle = '#2b2b2b'; ctx.font = F(46, 700);
  y = textBlock(ctx, note.title || items[0]?.name || 'Bản phối', x, y, colW, 56, 2) + 6;
  ctx.fillStyle = '#6b645a'; ctx.font = F(24);
  y = textBlock(ctx, `${character === 'male' ? 'Nam' : 'Nữ'}${ex.styleName ? ' · ' + ex.styleName : ''}${ex.eventName ? ' · ' + ex.eventName : ''}`, x, y + 8, colW, 32, 2) + 16;
  for (const it of items) {
    if (y > 1080) break;
    ctx.strokeStyle = '#2b2b2b'; ctx.lineWidth = 2; ctx.strokeRect(x, y + 4, 26, 26);
    ctx.fillStyle = '#6b645a'; ctx.font = F(20, 600); ctx.fillText(it.group.toUpperCase(), x + 42, y + 10);
    ctx.fillStyle = '#2b2b2b'; ctx.font = F(26, 600);
    let yy = textBlock(ctx, it.name, x + 42, y + 40, colW - 42, 32, 2);
    if (it.color) {
      ctx.fillStyle = it.color.hex; ctx.beginPath(); ctx.arc(x + 54, yy + 6, 12, 0, Math.PI * 2); ctx.fill();
      ctx.strokeStyle = 'rgba(0,0,0,.25)'; ctx.stroke();
      ctx.fillStyle = '#2b2b2b'; ctx.font = F(22); ctx.fillText(`${it.color.name} · ${it.color.hex}`, x + 74, yy + 14); yy += 30;
    }
    if (it.tip) { ctx.fillStyle = '#6b645a'; ctx.font = F(20); yy = textBlock(ctx, it.tip, x + 42, yy + 14, colW - 42, 26, 2); }
    y = yy + 18;
  }
  if (note.card && y < 1130) { ctx.fillStyle = '#8b2e1f'; ctx.font = F(28, 700); ctx.fillText(`${note.card.total}/100 · ${note.card.bandText}`, x, y + 20); }
  const cul = cultureLine(selection, ex.cultureCards);
  ctx.fillStyle = '#f1e9da'; ctx.fillRect(40, 1190, W - 80, 100);
  ctx.fillStyle = '#2b2b2b'; ctx.font = F(22);
  if (cul) textBlock(ctx, cul.text, 64, 1226, W - 128, 29, 2);
  ctx.fillStyle = '#6b645a'; ctx.font = F(18);
  ctx.fillText(['#VietPhuc', '#NepAo', '#VietPhucRemix'].join('  ') + (cul && !cul.verified ? '   · Thông tin văn hoá đang được kiểm chứng nguồn' : ''), 64, 1318);
  return cv;
}
export function downloadCanvas(cv: HTMLCanvasElement, name: string) {
  cv.toBlob(b => { if (!b) return; const a = document.createElement('a'); a.href = URL.createObjectURL(b); a.download = name; a.click(); setTimeout(() => URL.revokeObjectURL(a.href), 2000); }, 'image/png');
}
