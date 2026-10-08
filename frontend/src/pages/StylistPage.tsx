import { useEffect, useState } from 'react';
import { ArrowLeft, ArrowRight, Sparkles } from 'lucide-react';
import { ErrorBox, Loading, PageHeading, Stepper } from '../components/common/UI';
import { useActions } from '../ai/actions';
import { useStore } from '../ai/store';
import type { Answer } from '../ai/types';

/** Bước 1: bộ câu hỏi bối cảnh của AI Nếp Áo (dịp, thời tiết, nơi chụp, buổi, vai trò, phong cách, giới tính, màu) + lối tắt kể nhanh bằng một câu. */
export default function StylistPage() {
  const { quiz, answers, step, set, loading, loadError, reload } = useStore(); const { ask } = useActions();
  const [shortcut, setShortcut] = useState(''); const [text, setText] = useState(''); const [warn, setWarn] = useState('');
  const q = quiz[step];
  useEffect(() => { setText(answers[q?.id]?.text || ''); setWarn(''); }, [q?.id]); // eslint-disable-line

  if (loading) return <main className="page-container"><Stepper active={0} /><Loading text="Đang tải bộ câu hỏi…" /></main>;
  if (loadError || !q) return <main className="page-container"><Stepper active={0} /><ErrorBox message={loadError || 'Chưa tải được bộ câu hỏi.'} retry={reload} /></main>;

  const cur: Answer = answers[q.id] || {};
  const chosen = (v: string) => q.type === 'multi' ? ((cur.value as string[]) || []).includes(v) : cur.value === v;
  const withText = (all: Record<string, Answer>) => { const t = text.trim(); const a = { ...(all[q.id] || {}) }; if (t) a.text = t; else delete a.text; return { ...all, [q.id]: a }; };
  const pick = (v: string) => {
    const next: Answer = { ...cur };
    if (q.type === 'multi') { const s = new Set((cur.value as string[]) || []); if (s.has(v)) s.delete(v); else if (s.size < 3) s.add(v); next.value = [...s]; }
    else next.value = cur.value === v ? null : v;
    set({ answers: { ...answers, [q.id]: next } });
  };
  const submit = (all: Record<string, Answer>) => {
    const list = Object.entries(all).map(([questionId, v]) => ({ questionId, value: v.value || null, text: v.text || null }))
      .filter(a => (Array.isArray(a.value) ? a.value.length : a.value) || a.text);
    ask({ answers: list });
  };
  const go = (skip = false) => {
    let all = skip ? Object.fromEntries(Object.entries(answers).filter(([k]) => k !== q.id)) : withText(answers);
    const a = all[q.id];
    if (!skip && q.required && !((a?.value && (a.value as string[]).length) || a?.text)) { setWarn('Câu này cần chọn hoặc gõ câu trả lời.'); return; }
    if (a && !a.value && !a.text) { all = { ...all }; delete all[q.id]; }
    if (step === quiz.length - 1) { set({ answers: all }); submit(all); return; }
    set({ answers: all, step: step + 1 });
  };
  const summary = Object.entries(answers).map(([id, v]) => {
    const qq = quiz.find(x => x.id === id); if (!qq) return null;
    const labels = ([] as string[]).concat((v.value as string[]) || []).map(val => qq.options.find(o => o.value === val)?.label).filter(Boolean) as string[];
    if (v.text) labels.push(`“${v.text}”`);
    return labels.length ? <span className="tag" key={id}>{labels.join(', ')}</span> : null;
  });

  return <main className="page-container">
    <Stepper active={0} />
    <PageHeading eyebrow="AI VIỆT STYLIST" title="Cho stylist biết bối cảnh." description="Trả lời vài câu ngắn để stylist chọn đúng dịp, đúng thời tiết, đúng vai của bạn." />
    <div className="quiz-wrap">
      <form className="panel shortcut" onSubmit={e => { e.preventDefault(); if (shortcut.trim()) ask({ text: shortcut.trim() }); }}>
        <label htmlFor="shortcut">Lối tắt: kể nhanh bằng một câu</label>
        <div className="row"><input id="shortcut" value={shortcut} onChange={e => setShortcut(e.target.value)} placeholder="Ví dụ: chụp kỷ yếu ngoài trời tháng 12, nữ, thích nhẹ nhàng" />
          <button className="button dark" type="submit" disabled={!shortcut.trim()}>Gợi ý luôn <Sparkles size={16} /></button></div>
      </form>
      <section className="panel quiz-panel">
        <div className="progress"><div style={{ width: `${(step / quiz.length) * 100}%` }} /></div>
        <p className="muted">Câu {step + 1}/{quiz.length}{q.required ? ' · bắt buộc' : ' · có thể bỏ qua'}</p>
        <h2 className="qtitle">{q.question}</h2>
        <div className="chips">{q.options.map(o => <button type="button" key={o.value} className={`chip${chosen(o.value) ? ' selected' : ''}`} aria-pressed={chosen(o.value)} onClick={() => pick(o.value)}
          style={o.hex ? { borderLeft: `14px solid ${o.hex}` } : undefined}>{o.label}</button>)}</div>
        {q.placeholder && <input className="qtext" value={text} onChange={e => setText(e.target.value)} placeholder={q.placeholder} />}
        {warn && <p className="warn">{warn}</p>}
        <div className="quiz-actions">
          {step > 0 && <button className="button outline" onClick={() => set({ answers: withText(answers), step: step - 1 })}><ArrowLeft size={16} /> Quay lại</button>}
          {!q.required && <button className="button outline" onClick={() => go(true)}>Bỏ qua</button>}
          <button className="button primary" onClick={() => go()}>{step === quiz.length - 1 ? 'Xem 3 bộ gợi ý' : 'Tiếp'} <ArrowRight size={16} /></button>
        </div>
        <div className="tags summary">{summary}</div>
      </section>
    </div>
  </main>;
}
