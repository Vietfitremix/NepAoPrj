import type { WardrobeCharacter } from './maleWardrobe.ts';

export const characterViews = [
  { id: 'front', label: 'Trước', angle: 0 },
  { id: 'right', label: 'Phải', angle: 90 },
  { id: 'back', label: 'Sau', angle: 180 },
  { id: 'left', label: 'Trái', angle: 270 },
] as const;
export type CharacterView = typeof characterViews[number]['id'];
export const characterViewKey = 'viet-fit-character-view';

export function normalizeView(value: unknown): CharacterView {
  return characterViews.find(view => view.id === value)?.id ?? 'front';
}

export function rotateView(view: CharacterView, step: -1 | 1): CharacterView {
  const index = characterViews.findIndex(item => item.id === view);
  return characterViews[(index + step + characterViews.length) % characterViews.length].id;
}

export function characterBaseFile(_character: WardrobeCharacter, view: CharacterView): string {
  return `body/${view}.png`;
}

export function directionalGarmentFile(file: string, view: CharacterView): string {
  return file.slice(0, file.lastIndexOf('/') + 1) + `${view}.png`;
}

export function leftGarmentSourceFile(reference: string): string {
  return '/api/assets/' + reference.slice(0, reference.lastIndexOf('/') + 1) + 'left.png';
}
