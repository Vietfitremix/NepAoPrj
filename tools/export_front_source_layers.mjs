// Export the existing front fitting as independent aligned PNGs.
import { createRequire } from 'node:module';
import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import { getWardrobe } from '../frontend/src/utils/maleWardrobe.ts';
import { renderFrontLayers } from '../frontend/src/utils/renderMaleCharacter.ts';
const require = createRequire(new URL('../.tools/asset-qa/package.json', import.meta.url));
const { createCanvas, loadImage } = require('@napi-rs/canvas');
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
let count = 0;
for (const gender of ['male', 'female']) {
  const catalog = getWardrobe(gender);
  const directory = path.join(root, `frontend/public/figure/${gender}-layers`);
  await mkdir(directory, { recursive: true });
  const images = { [catalog.base]: createCanvas(1024, 1536) };
  for (const kind of ['outfits', 'pants', 'shoes']) for (const item of catalog[kind]) {
    if (item.sourcePrepared) continue;
    images[item.file] = await loadImage(await readFile(path.join(root, item.reference)));
    const canvas = createCanvas(1024, 1536);
    const selection = { shirt: null, pants: null, shoes: null };
    selection[kind === 'outfits' ? 'shirt' : kind] = item.id;
    renderFrontLayers(canvas.getContext('2d'), images, selection, gender);
    await writeFile(path.join(directory, item.file), canvas.toBuffer('image/png'));
    count++;
  }
}
console.log(`Exported ${count} independent front source layers.`);
