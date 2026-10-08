import { AlertCircle, ArrowRight, LoaderCircle, Sparkles } from 'lucide-react';
import { Link } from 'react-router-dom';
import type { ReactNode } from 'react';
export function Loading({ text = 'Đang chuẩn bị cho bạn…' }: { text?: string }) { return <div className="loading" role="status"><LoaderCircle className="spin" size={22}/><span>{text}</span></div>; }
export function ErrorBox({ message, retry }: { message: string; retry?: () => void }) { return <div className="error-box" role="alert"><AlertCircle size={20}/><div>{message}{retry && <button className="text-button" onClick={retry}>Thử lại <ArrowRight size={14}/></button>}</div></div>; }
export function EmptyState({ title, children }: { title: string; children: ReactNode }) { return <section className="empty-state"><Sparkles size={32}/><h2>{title}</h2><p>{children}</p><Link className="button primary" to="/stylist">Khám phá với AI <ArrowRight size={18}/></Link></section>; }
export function Stepper({ active }: { active: number }) { return <nav className="stepper" aria-label="Tiến trình tạo outfit">{['Bối cảnh', 'Gợi ý 3 bộ', 'Tuỳ chỉnh', 'Nhận xét'].map((label, i) => <div className={i === active ? 'active' : i < active ? 'done' : ''} key={label} aria-current={i === active ? 'step' : undefined}><span>{String(i + 1).padStart(2, '0')}</span><b>{label}</b></div>)}</nav>; }
export function PageHeading({ eyebrow, title, description }: { eyebrow: string; title: string; description: string }) { return <header className="page-heading"><span className="eyebrow">{eyebrow}</span><h1>{title}</h1><p>{description}</p></header>; }
