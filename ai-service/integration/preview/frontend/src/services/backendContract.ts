import type { MixConfig, Outfit, Look, Option } from '../types';
export interface Ref { code: string; name: string; description?: string }
export interface Summary extends Ref { thumbnailUrl: string | null; origin?: string; culturalMeaning?: string }
export interface Detail {
  outfit: Summary;
  colors: { code: string; name: string; hexCode: string }[];
  assets: { colorCode: string | null; assetType: string; variantCode: string | null; imageUrl: string; layerOrder: number }[];
  accessories: { code: string; name: string; imageUrl: string | null; layerOrder: number | null }[];
}
export interface ReferenceData { outfits: Detail[]; colors: Detail['colors']; styles: Ref[]; events: Ref[] }
export interface SavedLook {
  id: number; outfitCode: string; colorCode: string; styleCode: string; eventCode: string;
  accessories: string[]; styleMatchScore: number | null; culturalScore: number | null;
  colorHarmonyScore: number | null; previewImageUrl: string | null;
}
export const selection = (config: MixConfig) => ({ outfitCode: config.outfitCode, colorCode: config.colorCode,
  styleCode: config.styleCode, eventCode: config.eventCode, accessories: config.accessoryCodes });
export const options = (rows: Ref[]): Option[] => rows.map(r => ({ code: r.code, label: r.name }));
export const previewFor = (detail: Detail | undefined, color: string) => {
  const layer = detail?.assets.find(a => a.colorCode === color && a.assetType === 'GARMENT')?.imageUrl;
  return layer?.endsWith('-layer.svg') ? layer.replace('-layer.svg', '.svg') : detail?.outfit.thumbnailUrl || '';
};
export function outfitView(detail: Detail, styles: Ref[]): Outfit {
  return { code: detail.outfit.code, name: detail.outfit.name,
    baseAvatarUrl: detail.assets.find(a => a.assetType === 'BASE_AVATAR')?.imageUrl || '',
    assets: detail.assets.filter(a => a.assetType !== 'BASE_AVATAR').map((a, i) => ({ id: String(i),
      url: a.imageUrl, colorCode: a.colorCode || undefined, zIndex: a.layerOrder })),
    colors: detail.colors.map(c => ({ code: c.code, label: c.name, hex: c.hexCode })), styles: options(styles),
    accessories: detail.accessories.map(a => ({ code: a.code, label: a.name, assetUrl: a.imageUrl || '', zIndex: a.layerOrder ?? undefined })) };
}
export function lookView(data: SavedLook, refs: ReferenceData): Look {
  const outfit = refs.outfits.find(d => d.outfit.code === data.outfitCode)?.outfit;
  return { id: String(data.id), name: outfit?.name || data.outfitCode,
    imageUrl: data.previewImageUrl || '', outfitCode: data.outfitCode, outfitName: outfit?.name || data.outfitCode,
    styleName: refs.styles.find(s => s.code === data.styleCode)?.name || data.styleCode,
    eventName: refs.events.find(e => e.code === data.eventCode)?.name || data.eventCode,
    matchScore: data.styleMatchScore, culturalScore: data.culturalScore, colorHarmony: data.colorHarmonyScore,
    config: { conceptId: 'saved-' + data.id, outfitCode: data.outfitCode, colorCode: data.colorCode,
      styleCode: data.styleCode, eventCode: data.eventCode, accessoryCodes: data.accessories } };
}
