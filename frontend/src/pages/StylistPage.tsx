import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, ArrowRight, CloudSun, Sparkles } from 'lucide-react';
import { ErrorBox, Loading, PageHeading, Stepper } from '../components/common/UI';
import { getWeather } from '../services/weatherApi';
import { recommend } from '../services/recommendationApi';
import { errorMessage } from '../services/api';
import { useSession } from '../state';
import { answerLabels, quizPreferences, stylistQuiz } from '../utils/stylistQuiz';
import { resolvedPreferences } from '../utils/recommendationContext';
import type { QuizAnswer, Weather } from '../types';

export const events = [{code:'TET',label:'Tết'},{code:'FESTIVAL',label:'Lễ hội'},{code:'GRADUATION',label:'Kỷ yếu'},{code:'PHOTOSHOOT',label:'Chụp ảnh'},{code:'CULTURAL_EVENT',label:'Sự kiện văn hóa / cưới hỏi'}];
export const styles = [{code:'GEN_Z',label:'Gen Z'},{code:'MINIMAL',label:'Minimal'},{code:'ELEGANT',label:'Thanh lịch'},{code:'TRADITIONAL',label:'Truyền thống'},{code:'VINTAGE',label:'Hoài cổ'}];
export const cities = [{code:'Hanoi',label:'Hà Nội'},{code:'Ho Chi Minh City',label:'TP. Hồ Chí Minh'},{code:'Da Nang',label:'Đà Nẵng'},{code:'Hue',label:'Huế'}];
const weatherLabels: Record<string, string> = { RAIN:'Có mưa', SUNNY:'Trời nắng', CLEAR:'Trời quang', CLOUDS:'Nhiều mây', CLOUDY:'Nhiều mây', SNOW:'Có tuyết' };

export default function StylistPage() {
  const { session, update } = useSession();
  const previous = session.preferences;
  const navigate = useNavigate();
  const [step, setStep] = useState(0);
  const [answers, setAnswers] = useState<Record<string, QuizAnswer>>(previous?.answers || {});
  const [city, setCity] = useState(previous?.city || 'Hanoi');
  const [prompt, setPrompt] = useState(previous?.prompt || '');
  const [weather, setWeather] = useState<Weather>();
  const [weatherError, setWeatherError] = useState('');
  const [weatherRetry, setWeatherRetry] = useState(0);
  const [error, setError] = useState('');
  const [warning, setWarning] = useState('');
  const [busy, setBusy] = useState(false);
  const question = stylistQuiz[step];
  const current = answers[question.id] || {};
  const last = step === stylistQuiz.length - 1;
  useEffect(() => {
    const controller = new AbortController();
    setWeather(undefined); setWeatherError('');
    getWeather(city, controller.signal).then(data => { if (!controller.signal.aborted) setWeather(data); })
      .catch(err => { if (!controller.signal.aborted) setWeatherError(errorMessage(err)); });
    return () => controller.abort();
  }, [city, weatherRetry]);

  async function submit(all = answers) {
    if (!weather || busy) return;
    setBusy(true); setError('');
    const preferences = quizPreferences(all, prompt, city, weather);
    try {
      const recommendation = await recommend(preferences);
      if (!Array.isArray(recommendation.concepts) || recommendation.concepts.length !== 3)
        throw new Error('Máy chủ chưa trả về đủ 3 concept. Vui lòng thử lại.');
      update({ preferences: resolvedPreferences(preferences, recommendation), recommendation, mix:undefined });
      navigate('/concepts');
    } catch (err) { setError(errorMessage(err)); }
    finally { setBusy(false); }
  }
  function pick(value: string) {
    let next: QuizAnswer['value'];
    if (question.type === 'multi') {
      const selected = Array.isArray(current.value) ? current.value : [];
      if (selected.includes(value)) next = selected.filter(item=>item!==value);
      else if (selected.length < 3) next = [...selected, value];
      else { setWarning('Chọn tối đa 3 màu. Bỏ một màu để chọn màu khác.'); return; }
    } else next = current.value === value ? null : value;
    setAnswers({...answers,[question.id]:{...current,value:next}}); setWarning('');
  }
  function go(skip = false) {
    const all = {...answers};
    if (skip) delete all[question.id];
    if (!skip && question.required && !answerLabels(question,current).length) {
      setWarning('Câu này cần chọn hoặc gõ câu trả lời.'); return;
    }
    setAnswers(all); setWarning('');
    if (last) void submit(all); else setStep(value=>value+1);
  }
  return <main className="page-container nepao-page">
    <Stepper active={0}/>
    <PageHeading eyebrow="AI VIỆT STYLIST" title="Cho stylist biết bối cảnh." description="Trả lời 8 câu ngắn để stylist chọn đúng dịp, đúng thời tiết, đúng vai của bạn."/>
    <div className="quiz-wrap">
      <form className="panel shortcut" onSubmit={event => { event.preventDefault(); void submit(); }}>
        <label htmlFor="shortcut">Lối tắt: kể nhanh bằng một câu</label>
        <div className="row"><input id="shortcut" maxLength={1500} value={prompt} disabled={busy}
          onChange={event => setPrompt(event.target.value)} placeholder="Ví dụ: chụp kỷ yếu ngoài trời tháng 12, nam, thích nhẹ nhàng"/>
          <button className="button dark" type="submit" disabled={busy || !weather || !prompt.trim()}>
            {busy ? 'Đang gợi ý…' : 'Gợi ý luôn'} <Sparkles size={16}/>
          </button>
        </div><p className="form-note">Stylist dùng cả câu kể nhanh và những câu trả lời bạn đã chọn.</p>
      </form>
      <section className="panel quiz-panel">
        <div className="progress" role="progressbar" aria-label="Tiến trình trả lời" aria-valuenow={step + 1} aria-valuemin={1} aria-valuemax={stylistQuiz.length}>
          <div style={{width:`${((step + 1) / stylistQuiz.length) * 100}%`}}/>
        </div>
        <p className="muted">Câu {step + 1}/{stylistQuiz.length} · {question.required ? 'bắt buộc' : 'có thể bỏ qua'}</p>
        <h2 className="qtitle">{question.question}</h2>
        <div className="chips" role="group" aria-label="Chọn câu trả lời">
          {question.options.map(option=>{
            const chosen=Array.isArray(current.value)?current.value.includes(option.value):current.value===option.value;
            return <button type="button" key={option.value} className={`chip ${chosen?'selected':''}`} aria-pressed={chosen}
              disabled={busy} style={option.hex?{borderLeft:`14px solid ${option.hex}`}:undefined} onClick={()=>pick(option.value)}>{option.label}</button>;
          })}
        </div>
        {question.placeholder && <input className="qtext" aria-label={`Ghi thêm: ${question.question}`} maxLength={80}
          value={current.text || ''} disabled={busy} placeholder={question.placeholder}
          onChange={event=>{setAnswers({...answers,[question.id]:{...current,text:event.target.value}});setWarning('');}}/>}
        {question.id==='weather' && <div className="location-field"><label htmlFor="city">Thành phố của bạn</label>
          <select id="city" value={city} onChange={event=>setCity(event.target.value)} disabled={busy}>
            {cities.map(item=><option key={item.code} value={item.code}>{item.label}</option>)}
          </select><p className="form-note">Thời tiết hiện tại để tham khảo; bạn có thể chọn thời tiết dự kiến của buổi mặc.</p>
        </div>}
        <div className="quiz-weather" aria-live="polite">
          {weather ? <><CloudSun size={20}/><span>{cities.find(item=>item.code===city)?.label} · {Math.round(weather.temperature)}°C · {weatherLabels[weather.condition] || weather.condition}</span></>
            : weatherError ? <ErrorBox message={weatherError} retry={()=>setWeatherRetry(value=>value+1)}/>
              : <Loading text="Đang lấy thời tiết thực tế…"/>}
        </div>
        {warning && <p className="warn" role="alert">{warning}</p>}
        {error && <ErrorBox message={error}/>}
        <div className="quiz-actions">
          {step > 0 && <button className="button outline" disabled={busy} onClick={()=>{setStep(value=>value-1);setWarning('');}}><ArrowLeft size={16}/> Quay lại</button>}
          {!question.required && <button className="button outline" disabled={busy || (last && !weather)} onClick={()=>go(true)}>Bỏ qua</button>}
          <button className="button primary" disabled={busy || (last && !weather)} onClick={()=>go()}>
            {busy?'Stylist đang chọn đồ…':last?'Xem 3 bộ gợi ý':'Tiếp'} <ArrowRight size={16}/>
          </button>
        </div>
        <div className="tags summary">{stylistQuiz.map(item=>{
          const labels=answerLabels(item,answers[item.id]);
          return labels.length?<span className="tag" key={item.id}>{labels.join(', ')}</span>:null;
        })}</div>
      </section>
    </div>
  </main>;
}
