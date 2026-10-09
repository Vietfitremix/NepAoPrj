// Prepare imagegen clothing layers for the existing full-canvas avatars.
// Uses the project QA canvas dependency; does not generate substitute artwork.
import { createRequire } from 'node:module';
import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
const require = createRequire(new URL('../.tools/asset-qa/package.json', import.meta.url));
const { createCanvas, loadImage } = require('@napi-rs/canvas');
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const partial = process.argv.includes('--partial');
const records = [];
function bounds(data, from = 0, to = 1535, left = 0, right = 1023) {
  let x0 = 1024, x1 = -1, y0 = 1536, y1 = -1;
  for (let y = Math.max(0, Math.floor(from)); y <= Math.min(1535, Math.ceil(to)); y++)
    for (let x = left; x <= right; x++) {
      if (data[(y * 1024 + x) * 4 + 3] < 230) continue;
      x0 = Math.min(x0, x); x1 = Math.max(x1, x);
      y0 = Math.min(y0, y); y1 = Math.max(y1, y);
    }
  if (x1 < x0) throw new Error('Empty layer or invalid body region');
  return { x0, x1, y0, y1, width: x1 - x0 + 1, height: y1 - y0 + 1, center: (x0 + x1) / 2 };
}
async function imageData(file) {
  const image = await loadImage(await readFile(file));
  const canvas = createCanvas(1024, 1536), context = canvas.getContext('2d');
  context.drawImage(image, 0, 0, 1024, 1536);
  return { canvas, context, pixels: context.getImageData(0, 0, 1024, 1536) };
}
function runs(data, y) {
  const result = []; let start = -1;
  y = Math.max(0, Math.min(1535, Math.round(y)));
  for (let x = 0; x <= 1024; x++) {
    const opaque = x < 1024 && data[(y * 1024 + x) * 4 + 3] >= 230;
    if (opaque && start < 0) start = x;
    if (!opaque && start >= 0) { if (x-start >= 5) result.push([start,x]); start = -1; }
  }
  return result;
}
for (const gender of ['male', 'female']) {
  const catalog = JSON.parse(await readFile(path.join(root, `frontend/public/figure/${gender}-layers/catalog.json`), 'utf8'));
  const output = path.join(root, `frontend/public/figure/${gender}-layers`);
  await mkdir(output, { recursive: true });
  for (const view of ['right', 'left', 'back']) {
    const body = await imageData(path.join(root, `frontend/public/figure/${gender}-layers/body/${view}.png`));
    const torso = bounds(body.pixels.data, 300, 725);
    const hips = bounds(body.pixels.data, 650, 720, 340, 684);
    const feet = bounds(body.pixels.data, 1330, 1499);
    for (const kind of ['outfits', 'pants', 'shoes']) for (const item of catalog[kind]) {
      if (item.sourcePrepared) continue;
      const file = `${path.posix.dirname(item.file)}/${view}.png`;
      const rawPath = path.join(root, `assets/wardrobe/${gender}/${path.posix.dirname(item.file)}/source/${view}.png`);
      let raw;
      try { raw = await imageData(rawPath); }
      catch (error) { if (partial && error.code === 'ENOENT') continue; throw error; }
      const source = bounds(raw.pixels.data);
      // Eliminate generated background halos while keeping an antialiased edge.
      for (let i = 3; i < raw.pixels.data.length; i += 4) {
        const alpha = raw.pixels.data[i];
        raw.pixels.data[i] = alpha < 220 ? 0 : Math.round(Math.min(1, (alpha - 220) / 25) * 255);
      }
      raw.context.putImageData(raw.pixels, 0, 0);
      let scaleX, center, rows;
      if (kind === 'outfits') {
        const shape = bounds(raw.pixels.data, source.y0 + source.height * .12, source.y0 + source.height * .5);
        const extra = item.id === 'nhat-binh' ? (view === 'back' ? 130 : 55) : (view === 'back' ? 30 : 24);
        scaleX = (torso.width + extra) / shape.width;
        center = torso.center;
        const short = item.id === 'ba-ba';
        const top = short ? (view === 'back' ? 278 : 266)
          : view === 'back' ? (gender === 'male' ? 251 : 264)
          : gender === 'male' ? (view === 'right' ? 218 : 224) : 244;
        const hem = short ? 750
          : gender === 'male' ? (item.id === 'nhat-binh' ? 1190 : 1140) : 1230;
        const cuffFraction = short ? .9 : gender === 'female' ? (view === 'back' ? .40 : .43) : view === 'back' ? .54 : item.id === 'navy' ? .59 : .56;
        let cuffY = source.y0 + source.height * cuffFraction;
        if (view === 'back' && !short) {
          let started = false;
          for (let y = Math.round(source.y0+source.height*.2); y < source.y0+source.height*.65; y++) {
            const parts = runs(raw.pixels.data,y);
            if (parts.length === 3) { started = true; cuffY = y+1; }
            else if (started && parts.length === 1) break;
          }
        }
        rows = short ? [[source.y0,top],[source.y0+source.height*.1,302],[source.y1+1,hem]]
          : [[source.y0, top], [source.y0 + source.height * .1, 302], [cuffY, 735], [source.y1 + 1, hem]];
        // x translation uses the upper body's center, retaining panel flare.
        raw.fitCenter = shape.center;
      } else if (kind === 'pants') {
        scaleX = (hips.width + 14) / source.width;
        center = hips.center;
        rows = [[source.y0, 650], [source.y1 + 1, feet.y1 - 43]];
        raw.fitCenter = source.center;
      } else {
        scaleX = (feet.width + 20) / source.width;
        center = feet.center;
        rows = [[source.y0, feet.y1 - (item.id === 'sneakers' ? 95 : item.id === 'flats' ? 70 : 78)], [source.y1 + 1, feet.y1 + 6]];
        raw.fitCenter = source.center;
      }
      const canvas = createCanvas(1024, 1536), context = canvas.getContext('2d');
      context.imageSmoothingEnabled = true;
      context.imageSmoothingQuality = 'high';
      const x = center - raw.fitCenter * scaleX;
      for (let i = 1; i < rows.length; i++) {
        const [sy, dy] = rows[i - 1], [ey, ty] = rows[i];
        if (ey <= sy || ty <= dy) throw new Error(`Invalid fitted rows: ${file}`);
        if (kind !== 'pants') {
          if (kind === 'outfits') {
            const shapeRows = [];
            for (let y = Math.ceil(dy); y < ty; y++) {
              const sourceY = sy + (y-dy)/(ty-dy)*(ey-sy);
              let sourceRuns = runs(raw.pixels.data, sourceY), bodyRuns = runs(body.pixels.data,y);
              if (y >= 735 && sourceRuns.length === 3) sourceRuns = [sourceRuns[1]];
              if (y > 650 && sourceRuns.length === 1 && bodyRuns.length === 3) bodyRuns = [bodyRuns[1]];
              const knots = list => {
                if (list.length === 3) return list.flat();
                if (!list.length) return null;
                const lo=list[0][0], hi=list.at(-1)[1];
                return [0,.18,.25,.75,.82,1].map(t => lo+(hi-lo)*t);
              };
              const src=knots(sourceRuns), dst=knots(bodyRuns);
              const weight=Math.max(0,Math.min(1,(y-280)/70,(775-y)/60)) * (item.id === 'nhat-binh' && y > 430 ? .65 : 1);
              shapeRows.push({y,sourceY,src,target:src?.map((point,index) => (point*scaleX+x)*(1-weight)+((dst?.[index]??point*scaleX+x)+(index===0?-7:index===5?7:0))*weight)});
            }
            for (const [rowIndex,row] of shapeRows.entries()) {
              const {y,sourceY,src,target}=row;
              if (!src || !target || y < 280 || y >= 775) {
                const parts = runs(raw.pixels.data,sourceY);
                if(y >= 735 && y < 820 && parts.length === 3) {
                  const [lo,hi]=parts[1];context.drawImage(raw.canvas,lo,sourceY,hi-lo,(ey-sy)/(ty-dy),x+lo*scaleX,y,(hi-lo)*scaleX,1.25);
                } else context.drawImage(raw.canvas,0,sourceY,1024,(ey-sy)/(ty-dy),x,y,1024*scaleX,1.25);
                continue;
              }
              const neighbors=shapeRows.slice(Math.max(0,rowIndex-15),rowIndex+16).filter(entry=>entry.src&&entry.target);
              const smooth=key=>src.map((_,k)=>neighbors.reduce((sum,entry)=>sum+entry[key][k],0)/neighbors.length);
              const sourceKnots=smooth('src'), targetKnots=smooth('target');
              for(let k=1;k<6;k++) context.drawImage(raw.canvas,sourceKnots[k-1],sourceY,sourceKnots[k]-sourceKnots[k-1],(ey-sy)/(ty-dy),targetKnots[k-1],y,targetKnots[k]-targetKnots[k-1],1.25);
            }
            continue;
          }
          context.drawImage(raw.canvas, 0, sy, 1024, ey - sy, x, dy, 1024 * scaleX, ty - dy);
          continue;
        }
        // Fit trouser rows to the original hips and legs, including the wider
        // rear stance. A single global width leaves bare knees at the edges.
        for (let y = Math.ceil(dy); y < ty; y++) {
          const sourceY = sy + (y - dy) / (ty - dy) * (ey - sy);
          const sourceRow = bounds(raw.pixels.data, sourceY - 2, sourceY + 2);
          const bodyRow = bounds(body.pixels.data, y - 2, y + 2, 340, 684);
          const rowWidth = bodyRow.width + 16;
          context.drawImage(raw.canvas, sourceRow.x0, sourceY, sourceRow.width, (ey - sy) / (ty - dy),
            bodyRow.center - rowWidth / 2, y, rowWidth, 1.25);
        }
      }
      await writeFile(path.join(root, `frontend/public/figure/${gender}-layers/${file}`), canvas.toBuffer('image/png'));
      records.push({ gender, kind, id: item.id, view, raw: path.relative(root, rawPath).replaceAll('\\','/'),
        file, source, scaleX, x, rows });
    }
  }
}
await writeFile(path.join(root, 'assets/metadata/traditional-alignment.json'), JSON.stringify(records, null, 2));
console.log(`Aligned ${records.length}/57 independent source clothing layers.`);
