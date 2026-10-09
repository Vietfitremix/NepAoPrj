import type { MixConfig } from '../types';
import { getWardrobe, normalizeMaleSelection } from './maleWardrobe.ts';
import type { MaleSelection, WardrobeCharacter } from './maleWardrobe.ts';

const garments: Record<string, string> = {
  AO_TU_THAN: 'tu-than', AO_NGU_THAN: 'ngu-than', NHAT_BINH: 'nhat-binh', AO_BA_BA: 'ba-ba',
};
export const apiColorHex: Record<string, string> = {
  RED: '#b52838', DARK_RED: '#8b2635', WHITE: '#eee9dc', BLUE: '#32679e',
  YELLOW: '#e2b44b', BLACK: '#24242a', CREAM: '#fff4db',
};
export const apiAccessoryItems: Record<string, string[]> = {
  NON_LA: ['non-la'], NON_QUAI_THAO: ['non-quai-thao'], KHAN_VAN: ['khan-van'],
  KHAN_MO_QUA: ['khan-mo-qua'], KHAN_XEP: ['khan-xep'], HOA_CAI_TOC: ['hoa-cai-toc'],
  FAN: ['quat-giay'], QUAT_GIAY: ['quat-giay'], MINIMAL_BAG: ['tui-coi'], TUI: ['tui-coi'],
  KIENG_BAC: ['kieng-bac'], TRANG_SUC: ['bong-tai', 'vong-tay'],
};
export const apiFootwearItems: Record<string, string> = {
  WHITE_SNEAKERS: 'sneakers', SNEAKER: 'sneakers', GUOC: 'guoc', HAI_THEU: 'hai-theu',
  GIAY_BUP_BE: 'giay-bup-be', GIAY_TA: 'giay-ta',
};

// Translate the existing API selection into the local wardrobe for display only.
export function outfitPreview(config: Pick<MixConfig, 'outfitCode' | 'colorCode' | 'accessoryCodes'> & Partial<Pick<MixConfig, 'wardrobe'>>,
  character: WardrobeCharacter = config.wardrobe?.character ?? 'female'): MaleSelection | undefined {
  if (config.wardrobe) return normalizeMaleSelection(config.wardrobe.selection, character);
  const wardrobe = getWardrobe(character);
  const shirt = config.outfitCode === 'AO_DAI'
    ? (character === 'male' ? 'navy' : 'jade') : garments[config.outfitCode];
  if (!wardrobe.outfits.some(item => item.id === shirt)) return undefined;
  const selection: MaleSelection = {
    shirt, pants: 'ivory', shoes: null, accessories: {},
    styles: { shirt: { color: apiColorHex[config.colorCode] ?? null } },
  };
  for (const code of config.accessoryCodes) {
    if (code === 'QUAN_LUA') selection.pants = 'ivory';
    if (code === 'VAY_DUP' && character === 'female') {
      selection.pants = 'skirt-long-ivory';
      selection.styles!.pants = { color: '#24242a' };
    }
    if (code === 'VAY_XEP_LY' && character === 'female') selection.pants = 'skirt-short-navy';
    const shoe = apiFootwearItems[code];
    if (shoe && wardrobe.shoes.some(item => item.id === shoe)) selection.shoes = shoe;
    for (const id of apiAccessoryItems[code] ?? []) {
      const item = wardrobe.accessories.find(item => item.id === id);
      if (item?.slot) selection.accessories![item.slot] = id;
    }
  }
  return selection;
}
