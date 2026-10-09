import type { QuizAnswer } from '../types';

const choices: Record<string, readonly string[]> = {
  weather: ['nang_nong', 'mat_me', 'lanh', 'mua'],
  setting: ['ngoai_troi', 'trong_nha', 'ca_hai'],
  timeOfDay: ['ban_ngay', 'buoi_toi'],
  role: ['khach', 'nhan_vat_chinh', 'be_trap', 'nhom', 'chup_anh'],
};
/** Use the same known quiz answers for score, review and remix. */
export function reviewContext(answers?: Record<string, QuizAnswer>): Record<string, string> {
  return Object.fromEntries(Object.entries(choices).flatMap(([key, allowed]) => {
    const value = answers?.[key]?.value;
    return typeof value === 'string' && allowed.includes(value) ? [[key, value]] : [];
  }));
}

export const contextLabels: Record<string, string> = {
  weather: 'thời tiết', setting: 'không gian', timeOfDay: 'buổi', role: 'vai trò',
  nang_nong: 'nắng nóng', mat_me: 'mát mẻ', lanh: 'lạnh', mua: 'mưa',
  ngoai_troi: 'ngoài trời', trong_nha: 'trong nhà', ca_hai: 'cả trong và ngoài trời',
  ban_ngay: 'ban ngày', buoi_toi: 'buổi tối', khach: 'khách', nhan_vat_chinh: 'nhân vật chính',
  be_trap: 'bê tráp', nhom: 'nhóm', chup_anh: 'chụp ảnh',
};
