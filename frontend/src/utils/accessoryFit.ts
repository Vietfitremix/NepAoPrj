import type { WardrobeCharacter, WardrobeItem } from './maleWardrobe.ts';
import type { CharacterView } from './characterViews.ts';

type Raster = HTMLImageElement | HTMLCanvasElement;
export interface FitBox { x: number; y: number; width: number; height: number }
export interface AccessoryAnchors {
  head: FitBox; neck: FitBox; shoulders: FitBox; waist: FitBox; hands: FitBox[]; wrists: FitBox[];
}
interface Placement { crop: FitBox; target: FitBox }
export interface AccessoryCarrier { target: FitBox; id: string; slot?: string }
const W = 1024, H = 1536;
const center = (box: FitBox) => box.x + box.width / 2;
const box = (x: number, y: number, width: number, height: number): FitBox => ({ x, y, width, height });
function canvas(height = H, width = W) {
  const result = document.createElement('canvas'); result.width = width; result.height = height; return result;
}
function bounds(pixels: Uint8ClampedArray, area: FitBox, skin = false): FitBox | undefined {
  let left = W, top = H, right = -1, bottom = -1;
  for (let y = Math.max(0, Math.floor(area.y)); y < Math.min(H, Math.ceil(area.y + area.height)); y++)
    for (let x = Math.max(0, Math.floor(area.x)); x < Math.min(W, Math.ceil(area.x + area.width)); x++) {
      const i = (y * W + x) * 4;
      if (pixels[i + 3] < 200 || (skin && !(pixels[i] > pixels[i + 1] * 1.06 && pixels[i + 1] > pixels[i + 2] * 1.06))) continue;
      left = Math.min(left, x); right = Math.max(right, x); top = Math.min(top, y); bottom = Math.max(bottom, y);
    }
  return right >= left ? box(left, top, right - left + 1, bottom - top + 1) : undefined;
}
// Use the contiguous torso at the centre of the image, excluding the arms.
function torso(pixels: Uint8ClampedArray, y: number): FitBox {
  let left = 512, right = 512;
  while (left > 300 && pixels[(y * W + left - 1) * 4 + 3] > 230) left--;
  while (right < 724 && pixels[(y * W + right + 1) * 4 + 3] > 230) right++;
  return box(left, y, right - left + 1, 1);
}
const bodyCache = new WeakMap<Raster, Map<string, AccessoryAnchors>>();
export function measureAccessoryAnchors(body: Raster, character: WardrobeCharacter, view: CharacterView): AccessoryAnchors {
  let variants = bodyCache.get(body);
  if (!variants) { variants = new Map(); bodyCache.set(body, variants); }
  const key = character + '/' + view, cached = variants.get(key); if (cached) return cached;
  const source = canvas(), context = source.getContext('2d')!;
  context.drawImage(body, 0, 0, W, H);
  const pixels = context.getImageData(0, 0, W, H).data;
  const profile = view === 'left' || view === 'right';
  // Exclude the bun from head width: hats and glasses fit the skull, not the hairstyle.
  const headArea = profile ? box(view === 'left' ? 410 : 420, 0, 180, 215) : box(400, 0, 220, 215);
  const head = bounds(pixels, headArea) ?? box(435, 30, 155, 185);
  // The jaw still occupies row 225 in profile. Measure below it so the collar
  // follows the neck rather than the width and centre of the chin.
  const neck = bounds(pixels, box(400, 240, 220, 15), true) ?? box(470, 240, 85, 15);
  const areas = profile ? [box(view === 'left' ? 420 : 490, 728, 110, 152)]
    : [box(180, 728, 160, 152), box(690, 728, 155, 152)];
  const hands = areas.map(area => bounds(pixels, area, true) ?? area);
  const wrists = areas.map(area => bounds(pixels, { ...area, height: 16 }, true) ?? area);
  const result = { head, neck, shoulders: torso(pixels, 300), waist: torso(pixels, 660), hands, wrists };
  variants.set(key, result); return result;
}

// Geometry is expressed relative to the measured body; source crops retain their artwork.
export function accessoryTarget(item: WardrobeItem, anchors: AccessoryAnchors, view: CharacterView,
  aspect: number, part = 0, carrier?: AccessoryCarrier): FitBox {
  const { head, neck, shoulders, waist, hands, wrists } = anchors;
  const profile = view === 'left' || view === 'right', back = view === 'back';
  const cx = center(head), forehead = head.y + head.height * .28;
  const handIndex = profile ? 0 : item.slot === 'fan' ? (back ? 1 : 0) : (back ? 0 : 1);
  const hand = hands[handIndex], wrist = wrists[handIndex];
  switch (item.slot) {
    case 'headwear': {
      // Prepared sprites include the brim and were stretched during import.
      // Fit the crown's height to the skull instead of reusing that aspect ratio.
      let width = head.width * 1.05, height = head.height * .44, y = forehead - height * .93;
      if (item.id === 'non-la' || item.id === 'non-quai-thao') {
        width = head.width * (item.id === 'non-la' ? 2.05 : 2.65); height = width / aspect;
        y = forehead - height * (item.id === 'non-la' ? .63 : .23);
      } else if (item.id === 'mu-luoi-trai') {
        width = head.width * (profile ? 1.18 : 1.08); height = head.height * .42; y = forehead - height * .88;
      } else if (item.id === 'mu-cao-boi') {
        width = head.width * (profile ? 1.7 : 1.65); height = head.height * .6; y = forehead - height * .9;
      } else if (item.id === 'khan-mo-qua') {
        width = head.width * (profile ? 1.25 : 1.34);
        height = head.height * (view === 'front' ? 1.62 : 1.26); y = head.y - head.height * .02;
      } else if (item.id === 'khan-van') {
        width = head.width * 1.06; height = head.height * .26; y = head.y + head.height * .02;
      }
      return box(cx - width / 2, y, width, height);
    }
    case 'glasses': {
      const width = head.width * (profile ? .68 : .94), height = head.height * .19;
      return box(profile ? view === 'left' ? head.x - 2 : head.x + head.width - width + 2 : cx - width / 2,
        head.y + head.height * .45, width, height);
    }
    case 'headphones': {
      const earY = head.y + head.height * .5;
      if (part === 0) return box(profile ? cx - head.width * .09 : head.x - 3, head.y + 2,
        profile ? head.width * .18 : head.width + 6, earY - head.y + 5);
      const width = head.height * .24, height = head.height * .3;
      const earX = profile ? head.x + head.width * (view === 'left' ? .65 : .48)
        : part === 1 ? head.x + 2 : head.x + head.width - 2;
      return box(earX - width / 2, earY, width, height);
    }
    case 'hairAccessory': {
      const width = head.height * .2;
      const x = profile ? head.x + head.width * (view === 'left' ? .92 : .12)
        : head.x + head.width * (back ? .05 : .936);
      return box(x - width / 2, head.y + head.height * .27, width, width / aspect);
    }
    case 'earrings': {
      const width = head.height * .065;
      const x = profile ? head.x + head.width * (view === 'left' ? .65 : .48)
        : head.x + head.width * (part === 0 ? .05 : .95);
      return box(x - width / 2, head.y + head.height * .8, width, width / aspect);
    }
    case 'necklace': {
      const width = neck.width * (profile ? .98 : 1.18);
      return box(center(neck) - width / 2, neck.y + head.height * .04, width, head.height * (profile ? .15 : .17));
    }
    case 'bracelet': return box(wrist.x - 2, wrist.y + 5, wrist.width + 4, Math.min((wrist.width + 4) / aspect, wrist.width * .24));
    case 'gloves': {
      const h = hands[profile ? 0 : part], w = wrists[profile ? 0 : part];
      return box(h.x - 2, w.y, h.width + 4, h.height * .75);
    }
    case 'hipChain': {
      const width = waist.width * (profile ? .62 : .4);
      return box(profile ? waist.x + waist.width * .15 : back ? waist.x : waist.x + waist.width - width,
        waist.y + 5, width, width / aspect);
    }
    case 'backpack': {
      const width = shoulders.width * (profile ? 1.2 : .65), height = waist.y - shoulders.y;
      return box(profile ? view === 'left' ? shoulders.x + shoulders.width - width * .45 : shoulders.x - width * .55
        : center(shoulders) - width / 2, shoulders.y - 15, width, height);
    }
    case 'bag': {
      if (item.id === 'tui-deo-cheo') {
        const width = shoulders.width * (profile ? .9 : .95);
        return box(center(shoulders) - width / 2, shoulders.y - 15, width, waist.y - shoulders.y + 120);
      }
      const height = head.height * (item.id === 'tui-tote' ? 1.1 : item.id === 'tui-coi' ? 1.05 : .92);
      const width = height * aspect;
      return box(center(hand) - width / 2, hand.y + hand.height * .63, width, height);
    }
    case 'fan': {
      const width = head.height * (profile ? .11 : .95);
      return box(center(hand) - width * (back ? .4 : .6), hand.y + hand.height * .62,
        width, head.height * .98);
    }
    case 'bagCharm': {
      const width = head.height * .2;
      if (carrier) {
        const held = carrier.slot === 'bag' && carrier.id !== 'tui-deo-cheo';
        const u = view === 'back' || view === 'right' ? .2 : .8;
        return box(carrier.target.x + carrier.target.width * u - width / 2,
          carrier.target.y + carrier.target.height * (held ? .25 : carrier.slot === 'backpack' ? .72 : .82),
          width, width / aspect);
      }
      return box(back ? waist.x - width * .7 : waist.x + waist.width - width * .3, waist.y + 25, width, width / aspect);
    }
    default: return box(0, 0, W, H);
  }
}

interface FittedAccessory { image: Raster; offsetX: number; offsetY: number; target?: FitBox; rearImage?: Raster }
export function nonLaGeometry(anchors: AccessoryAnchors, view: CharacterView, crownCrop: FitBox, strapCrop: FitBox) {
  const {head} = anchors, profile = view === 'left' || view === 'right';
  const width = head.width * (profile ? 1.95 : 1.9), scale = width / crownCrop.width;
  const height = crownCrop.height * scale;
  const seat = head.y + head.height * (profile ? .3 : view === 'back' ? .16 : .23);
  const crown = box(center(head) - width / 2, seat - height, width, height);
  const strapY = crown.y + (strapCrop.y - crownCrop.y) * scale;
  const chinY = head.y + head.height * (view === 'back' ? 1.08 : 1.22);
  const strap = box(crown.x + (strapCrop.x - crownCrop.x) * scale, strapY,
    strapCrop.width * scale, chinY - strapY);
  const chinX = profile ? head.x + head.width * (view === 'left' ? .24 : .76) : center(head);
  return {crown, strap, chinX};
}

function fitNonLa(pixels: Uint8ClampedArray, anchors: AccessoryAnchors,
  view: CharacterView): FittedAccessory | undefined {
  // The burgundy fabric has a different colour from the straw. Separate it
  // before fitting so extending a chin strap cannot stretch the cone or brim.
  const crownSource = canvas(), strapSource = canvas();
  const crownContext = crownSource.getContext('2d')!, strapContext = strapSource.getContext('2d')!;
  let crownPixels = crownContext.createImageData(W, H);
  const strapPixels = strapContext.createImageData(W, H);
  for (let i = 0; i < pixels.length; i += 4) {
    if (!pixels[i + 3]) continue;
    const fabric = pixels[i] > pixels[i + 1] * 1.55 && pixels[i + 2] > pixels[i + 1] * 1.05;
    (fabric ? strapPixels.data : crownPixels.data).set(pixels.subarray(i, i + 4), i);
  }
  if (view === 'left' || view === 'right') {
    // Restore the straw hidden by the old knot before moving that knot. The
    // brim is continuous, so its lower edge interpolates across the ribbon.
    const edges = new Int32Array(W).fill(-1), firstRed = new Int32Array(W).fill(H);
    for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) {
      const i = (y * W + x) * 4;
      if (crownPixels.data[i + 3] > 200) edges[x] = y;
      if (strapPixels.data[i + 3] > 200) firstRed[x] = Math.min(firstRed[x], y);
    }
    for (let x = 0; x < W; x++) {
      if (firstRed[x] === H || firstRed[x] > edges[x] + 3) continue;
      let l = x - 1, r = x + 1;
      while (l >= 0 && (edges[l] < 0 || firstRed[l] <= edges[l] + 3)) l--;
      while (r < W && (edges[r] < 0 || firstRed[r] <= edges[r] + 3)) r++;
      if (l < 0 || r >= W || r - l > 100) continue;
      const u = (x - l) / (r - l), edge = Math.round(edges[l] * (1 - u) + edges[r] * u);
      for (let y = firstRed[x]; y <= edge; y++) {
        const i = (y * W + x) * 4; if (!strapPixels.data[i + 3]) continue;
        const li = (Math.min(y, edges[l]) * W + l) * 4, ri = (Math.min(y, edges[r]) * W + r) * 4;
        for (let c = 0; c < 3; c++) crownPixels.data[i + c] = crownPixels.data[li + c] * (1 - u) + crownPixels.data[ri + c] * u;
        crownPixels.data[i + 3] = pixels[i + 3];
      }
    }
  }
  crownContext.putImageData(crownPixels, 0, 0);
  if (view === 'left' || view === 'right') {
    const crop = bounds(crownPixels.data, box(0, 0, W, H))!;
    const lx = Math.round(crop.x + crop.width * .2), rx = Math.round(crop.x + crop.width * .8);
    const l = bounds(crownPixels.data, box(lx, crop.y, 1, crop.height));
    const r = bounds(crownPixels.data, box(rx, crop.y, 1, crop.height));
    if (l && r) {
      // Level the side-view brim before seating it on the skull. A diagonal
      // brim from the source otherwise floats above the forehead.
      const slope = (r.y + r.height - l.y - l.height) / (rx - lx);
      const levelled = canvas(), lc = levelled.getContext('2d')!;
      lc.transform(1, -slope, 0, 1, 0, slope * center(crop)); lc.drawImage(crownSource, 0, 0);
      crownPixels = lc.getImageData(0, 0, W, H);
    }
  }
  const crownCrop = bounds(crownPixels.data, box(0, 0, W, H));
  const strapCrop = bounds(strapPixels.data, box(0, 0, W, H));
  if (!crownCrop || !strapCrop) return;
  crownContext.putImageData(crownPixels, 0, 0); strapContext.putImageData(strapPixels, 0, 0);
  const {crown, strap, chinX} = nonLaGeometry(anchors, view, crownCrop, strapCrop);
  const strapBottom = bounds(strapPixels.data,
    box(strapCrop.x, strapCrop.y + strapCrop.height * .94, strapCrop.width, strapCrop.height * .06))!;
  const profile = view === 'left' || view === 'right';
  const strapTop = bounds(strapPixels.data,
    box(strapCrop.x, strapCrop.y, strapCrop.width, strapCrop.height * .04))!;
  let pivot = strap.x + (center(strapTop) - strapCrop.x) / strapCrop.width * strap.width;
  if (profile) {
    // The generated side sprites tie the ribbon near the nose. Move that
    // attachment along the actual brim to above the visible ear.
    const earX = anchors.head.x + anchors.head.width * (view === 'left' ? .65 : .48);
    const column = Math.round(crownCrop.x + (earX - crown.x) / crown.width * crownCrop.width);
    const brim = bounds(crownPixels.data, box(column - 2, crownCrop.y, 5, crownCrop.height));
    const chinY = strap.y + strap.height;
    strap.x += earX - pivot; pivot = earX;
    if (brim) strap.y = crown.y + (brim.y + brim.height - crownCrop.y) / crownCrop.height * crown.height - 3;
    strap.height = chinY - strap.y;
  }
  const bottomSqueeze = profile ? .65 : 1;
  const originalBottomX = strap.x + (center(strapBottom) - strapCrop.x) / strapCrop.width * strap.width;
  const originalChinX = pivot + (originalBottomX - pivot) * bottomSqueeze;
  const shift = chinX - originalChinX;
  const left = Math.floor(Math.min(crown.x, strap.x, strap.x + shift)) - 2;
  const right = Math.ceil(Math.max(crown.x + crown.width, strap.x + strap.width, strap.x + strap.width + shift)) + 2;
  const top = Math.floor(Math.min(crown.y, strap.y)) - 2, bottom = Math.ceil(strap.y + strap.height) + 2;
  const fitted = canvas(bottom - top, right - left), context = fitted.getContext('2d')!;
  context.translate(-left, -top); context.imageSmoothingEnabled = true; context.imageSmoothingQuality = 'high';
  const rearImage = profile ? canvas(bottom - top, right - left) : undefined;
  const rearContext = rearImage?.getContext('2d');
  rearContext?.translate(-left, -top);
  // The attachment stays at the brim. Only the lower loop moves towards the
  // visible chin in a profile, instead of hanging vertically beside the ear.
  for (let row = 0; row < strapCrop.height; row++) {
    const u = row / strapCrop.height, bend = u * u * (3 - 2 * u);
    const squeeze = 1 - (1 - bottomSqueeze) * bend;
    const dx = pivot + (strap.x - pivot) * squeeze + shift * bend, dy = strap.y + u * strap.height;
    const dw = strap.width * squeeze, dh = strap.height / strapCrop.height + .35;
    if (rearContext) rearContext.drawImage(strapSource, strapCrop.x, strapCrop.y + row, strapCrop.width, 1, dx, dy, dw, dh);
    // Follow the transparent gap between the two ribbons. A percentage cut
    // would leave a square edge where the ribbons curve into the lower loop.
    let visible = box(strapCrop.x, strapCrop.y + row, strapCrop.width, 1);
    if (profile) {
      const runs: FitBox[] = [];
      let start = -1;
      for (let x = strapCrop.x; x <= strapCrop.x + strapCrop.width; x++) {
        const occupied = x < strapCrop.x + strapCrop.width && strapPixels.data[((strapCrop.y + row) * W + x) * 4 + 3] > 80;
        if (occupied && start < 0) start = x;
        if (!occupied && start >= 0) { runs.push(box(start, strapCrop.y + row, x - start, 1)); start = -1; }
      }
      const near = view === 'left' ? runs[0] : runs[runs.length - 1];
      if (!near) continue;
      visible = box(Math.max(strapCrop.x, near.x - 1), near.y, Math.min(strapCrop.width, near.width + 2), 1);
    }
    context.drawImage(strapSource, visible.x, visible.y, visible.width, 1,
      dx + (visible.x - strapCrop.x) / strapCrop.width * dw, dy, visible.width / strapCrop.width * dw, dh);
  }
  context.drawImage(crownSource, crownCrop.x, crownCrop.y, crownCrop.width, crownCrop.height,
    crown.x, crown.y, crown.width, crown.height);
  return {image: fitted, rearImage, offsetX: left, offsetY: top, target: box(left, top, right - left, bottom - top)};
}
const cache = new WeakMap<Raster, WeakMap<Raster, Map<string, FittedAccessory>>>();
export function fitAccessory(image: Raster, body: Raster, item: WardrobeItem, character: WardrobeCharacter,
  view: CharacterView, carrier?: AccessoryCarrier): FittedAccessory {
  if (typeof document === 'undefined' || !image.width || !body?.width || !item.slot)
    return { image, offsetX: 0, offsetY: item.offsetY ?? 0 };
  let byBody = cache.get(image); if (!byBody) { byBody = new WeakMap(); cache.set(image, byBody); }
  let variants = byBody.get(body); if (!variants) { variants = new Map(); byBody.set(body, variants); }
  const key = character + '/' + view + '/' + item.id + '/' + JSON.stringify(carrier);
  const cached = variants.get(key); if (cached) return cached;
  const source = canvas(), sc = source.getContext('2d')!; sc.drawImage(image, 0, 0, W, H);
  const pixels = sc.getImageData(0, 0, W, H).data;
  const full = bounds(pixels, box(0, 0, W, H)); if (!full) return { image, offsetX: 0, offsetY: item.offsetY ?? 0 };
  const anchors = measureAccessoryAnchors(body, character, view), placements: Placement[] = [];
  if (item.id === 'non-la') {
    const fitted = fitNonLa(pixels, anchors, view);
    if (fitted) { variants.set(key, fitted); return fitted; }
  }
  const profile = view === 'left' || view === 'right';
  const add = (crop: FitBox | undefined, part = 0) => {
    if (!crop) return;
    const target = accessoryTarget(item, anchors, view, crop.width / crop.height, part, carrier);
    if (item.slot === 'fan' || (item.slot === 'bag' && item.id !== 'tui-deo-cheo')) {
      // The handle is not necessarily centred in a turned or tilted source.
      // Anchor its actual top pixels to the fingers, not the image rectangle.
      const grip = bounds(pixels, box(crop.x, crop.y, crop.width, Math.max(2, crop.height * .07)));
      const index = profile ? 0 : item.slot === 'fan' ? (view === 'back' ? 1 : 0) : (view === 'back' ? 0 : 1);
      if (grip) target.x = center(anchors.hands[index]) - (center(grip) - crop.x) / crop.width * target.width;
    }
    placements.push({ crop, target });
  };
  if ((item.slot === 'earrings' || item.slot === 'gloves') && !profile) {
    add(bounds(pixels, box(0, 0, W / 2, H)), 0); add(bounds(pixels, box(W / 2, 0, W / 2, H)), 1);
  } else if (item.slot === 'headphones') {
    const splitY = character === 'male' ? 116 : 128;
    add(bounds(pixels, box(0, 0, W, splitY)), 0);
    if (profile) add(bounds(pixels, box(0, splitY, W, H - splitY)), 1);
    else {
      add(bounds(pixels, box(0, splitY, W / 2, H - splitY)), 1);
      add(bounds(pixels, box(W / 2, splitY, W / 2, H - splitY)), 2);
    }
  } else add(full);
  if (!placements.length) return { image, offsetX: 0, offsetY: item.offsetY ?? 0 };
  // Cache only the occupied region; cycling through the wardrobe should not
  // retain a full 1024x1736 canvas for every small earring or bracelet.
  const left = Math.floor(Math.min(...placements.map(({target})=>target.x))) - 1;
  const top = Math.floor(Math.min(...placements.map(({target})=>target.y))) - 1;
  const right = Math.ceil(Math.max(...placements.map(({target})=>target.x+target.width))) + 1;
  const bottom = Math.ceil(Math.max(...placements.map(({target})=>target.y+target.height))) + 1;
  const fitted = canvas(bottom - top, right - left), context = fitted.getContext('2d')!;
  context.translate(-left, -top);
  context.imageSmoothingEnabled = true; context.imageSmoothingQuality = 'high';
  for (const { crop, target } of placements) {
    if (item.id === 'khan-mo-qua' && view === 'front') {
      // Keep the crown fitted while lengthening the opening to the chin.
      // Scaling the entire hood puts its bow over the avatar's mouth.
      const split = .32, crownHeight = anchors.head.height * 1.26 * split;
      context.drawImage(source, crop.x, crop.y, crop.width, crop.height * split,
        target.x, target.y, target.width, crownHeight);
      context.drawImage(source, crop.x, crop.y + crop.height * split, crop.width, crop.height * (1 - split),
        target.x, target.y + crownHeight, target.width, target.height - crownHeight);
    } else context.drawImage(source, crop.x, crop.y, crop.width, crop.height,
      target.x, target.y, target.width, target.height);
  }
  if (item.slot === 'gloves') {
    const bodyCanvas = canvas(), bodyContext = bodyCanvas.getContext('2d')!;
    bodyContext.drawImage(body, 0, 0, W, H);
    const skin = bodyContext.getImageData(0, 0, W, H).data;
    const glove = context.getImageData(0, 0, fitted.width, fitted.height);
    for (let y = 0; y < fitted.height; y++) for (let x = 0; x < fitted.width; x++) {
      const i = (y * fitted.width + x) * 4; if (!glove.data[i + 3]) continue;
      let covered = false;
      for (let dy = -2; dy <= 2 && !covered; dy++) for (let dx = -2; dx <= 2; dx++) {
        const bx = x + left + dx, by = y + top + dy;
        if (bx < 0 || bx >= W || by < 0 || by >= H) continue;
        const j = (by * W + bx) * 4;
        if (skin[j + 3] > 200 && skin[j] > skin[j + 1] * 1.06 && skin[j + 1] > skin[j + 2] * 1.06) { covered = true; break; }
      }
      if (!covered) glove.data[i + 3] = 0;
    }
    context.putImageData(glove, 0, 0);
  }
  const result = { image: fitted, offsetX: left, offsetY: top, target: placements[0]?.target };
  variants.set(key, result); return result;
}
