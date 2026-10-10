import type { Preferences, QuizAnswer, Weather } from '../types';
import { wardrobeColors } from './wardrobeStyles.ts';

export interface QuizQuestion {
  id: string; question: string; type: 'single' | 'multi'; required?: boolean;
  options: { value: string; label: string; hex?: string }[]; placeholder?: string;
}

// The eight context questions from NepAoPrj, using the existing wardrobe palette.
export let stylistQuiz: QuizQuestion[] = [
  { id: 'occasion', question: 'Bạn sẽ mặc Việt phục vào dịp nào?', type: 'single', required: true,
    options: [{ value:'tet', label:'Tết / du xuân' }, { value:'ky_yeu', label:'Chụp kỷ yếu / tốt nghiệp' },
      { value:'dam_cuoi', label:'Đám cưới, ăn hỏi' }, { value:'le_hoi_chua', label:'Lễ hội / đi chùa' },
      { value:'dao_pho', label:'Dạo phố / chụp ảnh' }], placeholder:'Hoặc kể dịp của bạn, ví dụ: đi hội làng cuối tuần' },
  { id:'weather', question:'Thời tiết hôm đó thế nào?', type:'single',
    options:[{value:'nang_nong',label:'Nắng nóng'},{value:'mat_me',label:'Mát mẻ'},
      {value:'lanh',label:'Se lạnh / lạnh'},{value:'mua',label:'Có mưa'}], placeholder:'Ví dụ: tháng 12 ở Hà Nội, trời hanh' },
  { id:'setting', question:'Bạn ở trong nhà hay ngoài trời?', type:'single',
    options:[{value:'ngoai_troi',label:'Ngoài trời'},{value:'trong_nha',label:'Trong nhà'},{value:'ca_hai',label:'Cả hai'}],
    placeholder:'Ví dụ: chụp ở công viên rồi vào nhà hàng' },
  { id:'timeOfDay', question:'Vào buổi nào?', type:'single',
    options:[{value:'ban_ngay',label:'Ban ngày'},{value:'buoi_toi',label:'Buổi tối'}], placeholder:'Ví dụ: tiệc tối' },
  { id:'role', question:'Bạn tham gia với vai trò gì?', type:'single',
    options:[{value:'khach',label:'Khách mời'},{value:'nhan_vat_chinh',label:'Nhân vật chính (cô dâu, chú rể, người tốt nghiệp…)'},
      {value:'be_trap',label:'Bê tráp / phụ dâu, phụ rể'},{value:'nhom',label:'Đi cùng nhóm / cả lớp'},
      {value:'chup_anh',label:'Đi chơi, chụp ảnh'}], placeholder:'Ví dụ: mình là phù dâu' },
  { id:'style', question:'Bạn thích phong cách nào?', type:'single',
    options:[{value:'truyen_thong',label:'Truyền thống'},{value:'toi_gian',label:'Tối giản'},
      {value:'duong_pho',label:'Đường phố, cá tính'},{value:'pastel',label:'Pastel, nhẹ nhàng'}],
    placeholder:'Ví dụ: nhẹ nhàng nhưng vẫn nổi bật' },
  { id:'gender', question:'Người mặc là nam hay nữ?', type:'single',
    options:[{value:'nu',label:'Nữ'},{value:'nam',label:'Nam'}] },
  { id:'colors', question:'Màu bạn thích? (chọn tối đa 3, có thể bỏ qua)', type:'multi',
    options:wardrobeColors.map(color=>({value:color.value,label:color.name,hex:color.value})),
    placeholder:'Ví dụ: thích tông ấm, không thích màu hồng' },
];
export function setStylistQuiz(questions:QuizQuestion[]) {
 if(!Array.isArray(questions) || !questions.length || questions.some(q=>!q.id || !Array.isArray(q.options)))
  throw new Error('Bộ câu hỏi trên máy chủ chưa đầy đủ.');
 stylistQuiz=questions;
}

export function answerLabels(question: QuizQuestion, answer?: QuizAnswer): string[] {
  const values = Array.isArray(answer?.value) ? answer.value : answer?.value ? [answer.value] : [];
  const labels = values.map(value=>question.options.find(option=>option.value===value)?.label).filter((label):label is string=>!!label);
  if (answer?.text?.trim()) labels.push(answer.text.trim());
  return labels;
}

// Nhãn ngắn cho từng câu hỏi. Không đưa nguyên câu hỏi vào lời nhắn: câu "(có thể bỏ qua)" từng bị hiểu nhầm là
// "bỏ màu", làm màu đầu tiên người dùng chọn bị loại khỏi gợi ý.
const contextLabels: Record<string, string> = {
  occasion:'Dịp', weather:'Thời tiết', setting:'Nơi mặc', timeOfDay:'Buổi', role:'Vai trò',
  style:'Phong cách ưa thích', gender:'Người mặc', colors:'Màu ưa thích',
};
export function quizContext(answers: Record<string, QuizAnswer>): string {
  return stylistQuiz.map(question=>{
    const labels=answerLabels(question,answers[question.id]);
    return labels.length ? `${contextLabels[question.id]||question.id}: ${labels.join(', ')}` : '';
  }).filter(Boolean).join('. ');
}

export const quizColorCodes: Record<string, string> = {'#b52838':'RED','#de91aa':'PINK','#e2b44b':'YELLOW','#39705b':'GREEN','#32679e':'BLUE',
  '#765a94':'PURPLE','#876044':'BROWN','#eee9dc':'WHITE','#24242a':'BLACK'};

export function quizPreferences(answers: Record<string, QuizAnswer>, prompt: string, city: string, weather: Weather): Preferences {
  const events:Record<string,string>={tet:'TET',ky_yeu:'GRADUATION',dam_cuoi:'CULTURAL_EVENT',le_hoi_chua:'FESTIVAL',dao_pho:'PHOTOSHOOT'};
  const styles:Record<string,string>={truyen_thong:'TRADITIONAL',toi_gian:'MINIMAL',duong_pho:'GEN_Z',pastel:'ELEGANT'};
  const firstColor=Array.isArray(answers.colors?.value)?answers.colors.value[0]:undefined;
  return {prompt:prompt.trim(),city,weather,answers,character:answers.gender?.value==='nam'?'male':'female',
    eventCode:events[String(answers.occasion?.value)]||'TET',styleCode:styles[String(answers.style?.value)]||'GEN_Z',
    colorCode:quizColorCodes[firstColor||'']||'ANY'};
}
