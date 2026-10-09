import { useEffect, useRef, useState } from 'react';
import { ImageOff } from 'lucide-react';
import { assetRoot, getWardrobe, selectedWardrobeItems } from '../../utils/maleWardrobe';
import type { MaleSelection, WardrobeCharacter } from '../../utils/maleWardrobe';
import { characterBaseFile, directionalGarmentFile, leftGarmentSourceFile } from '../../utils/characterViews';
import type { CharacterView } from '../../utils/characterViews';
import { renderMaleCharacter, characterHeadroom } from '../../utils/renderMaleCharacter';
import { withHandForeground } from '../../utils/sourceDirectionRenderer';
import type { CharacterImages } from '../../utils/sourceDirectionRenderer';
import { patternFile } from '../../utils/wardrobeStyles';

const imageCache = new Map<string, Promise<HTMLImageElement>>();
const baseCache = new Map<string, Promise<CharacterImages>>();
function loadImage(url: string) {
  let promise = imageCache.get(url);
  if (!promise) {
    promise = new Promise<HTMLImageElement>((resolve, reject) => {
      const image = new Image();
      image.onload = () => resolve(image);
      image.onerror = () => { imageCache.delete(url); reject(new Error('Không tải được hình trang phục.')); };
      image.src = url;
    });
    imageCache.set(url, promise);
  }
  return promise;
}
function loadBase(character: WardrobeCharacter, view: CharacterView) {
  const key = character + '/' + view;
  let promise = baseCache.get(key);
  if (!promise) {
    const file = characterBaseFile(character, view);
    promise = loadImage(assetRoot(character) + file).then(image => withHandForeground({ [file]: image }, character))
      .catch(error => { baseCache.delete(key); throw error; });
    baseCache.set(key, promise);
  }
  return promise;
}

/** Vẽ người mẫu đã mặc đồ lên một canvas (dùng cho hình trong studio và cho thẻ Lookbook). Từ chối (reject) nếu không tải được hình. */
export async function paintWardrobe(canvas: HTMLCanvasElement, selection: MaleSelection, character: WardrobeCharacter,
  view: CharacterView, cancelled: () => boolean = () => false) {
  const context = canvas.getContext('2d');
  if (!context) throw new Error('Canvas không khả dụng.');
  context.clearRect(0, 0, canvas.width, canvas.height);
  const files = selectedWardrobeItems(selection, character).map(item => directionalGarmentFile(item.file, view));
  const shirt = getWardrobe(character).outfits.find(item => item.id === selection.shirt);
  if (view === 'left' && shirt) files.push(leftGarmentSourceFile(shirt.reference));
  files.push(...Object.values(selection.styles ?? {}).map(patternFile).filter((file): file is string => !!file));
  const [base, layers] = await Promise.all([
    loadBase(character, view),
    Promise.all([...new Set(files)].map(async file => [file, await loadImage(
      file.startsWith('/api/assets/') ? file : (file.startsWith('patterns/') ? '/figure/' : assetRoot(character)) + file,
    )] as const)),
  ]);
  if (cancelled()) return;
  renderMaleCharacter(context, { ...base, ...Object.fromEntries(layers) }, selection, character, view);
}

export default function WardrobeFigure({ selection, character = 'female', view = 'front', label, className = '' }: {
  selection?: MaleSelection; character?: WardrobeCharacter; view?: CharacterView; label: string; className?: string;
}) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [status, setStatus] = useState<'loading' | 'ready' | 'error'>('loading');
  const [retry, setRetry] = useState(0);
  const signature = JSON.stringify(selection);
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || !selection) return;
    let cancelled = false;
    setStatus('loading');
    paintWardrobe(canvas, selection, character, view, () => cancelled)
      .then(() => { if (!cancelled) setStatus('ready'); })
      .catch(() => { if (!cancelled) setStatus('error'); });
    return () => { cancelled = true; };
    // The signature tracks the complete display selection without refetching for object identity changes.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [signature, character, view, retry]);
  const wardrobe = getWardrobe(character);
  return <div className={`wardrobe-figure ${className}`} aria-busy={!!selection && status === 'loading'}>
    <canvas ref={canvasRef} width={wardrobe.width} height={wardrobe.height + characterHeadroom}
      role="img" aria-label={label} hidden={!selection || status !== 'ready'} />
    {!selection || status === 'error' ? <div className="figure-placeholder"><ImageOff size={24}/>
      <p>Chưa có hình cho bản phối này.</p>{selection && <button type="button" className="text-button" onClick={() => setRetry(value => value + 1)}>Thử lại</button>}
    </div> : status === 'loading' && <span className="figure-placeholder" role="status">Đang tải trang phục…</span>}
  </div>;
}
