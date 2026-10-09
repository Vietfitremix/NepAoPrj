import { Component } from 'react';
import type { ReactNode } from 'react';
import { Route, Routes } from 'react-router-dom';
import { SessionProvider } from './state';
import Header from './components/common/Header';
import Footer from './components/common/Footer';
import { EmptyState } from './components/common/UI';
import HomePage from './pages/HomePage';
import StylistPage from './pages/StylistPage';
import ConceptPage from './pages/ConceptPage';
import MixStudioPage from './pages/MixStudioPage';
import FinalLookPage from './pages/FinalLookPage';
import MaleStudioPage from './pages/MaleStudioPage';
import DatabaseDataGate from './components/common/DatabaseDataGate';
class ErrorBoundary extends Component<{children:ReactNode},{failed:boolean}>{state={failed:false};static getDerivedStateFromError(){return {failed:true};}render(){return this.state.failed?<main className="empty-state"><h1>Chưa thể hiển thị trang này.</h1><p>Dữ liệu phiên có thể không còn tương thích. Hãy bắt đầu lại.</p><button className="button primary" onClick={()=>{try{sessionStorage.removeItem('viet-fit-session');}catch{/* Storage may be unavailable. */}window.location.assign('/');}}>Về trang chủ</button></main>:this.props.children;}}
export default function App(){return <ErrorBoundary><DatabaseDataGate><SessionProvider><a href="#main-content" className="skip-link">Đến nội dung chính</a><Header/><div id="main-content"><Routes><Route path="/" element={<HomePage/>}/><Route path="/stylist" element={<StylistPage/>}/><Route path="/male-studio" element={<MaleStudioPage key="male"/>}/><Route path="/female-studio" element={<MaleStudioPage key="female" initialCharacter="female"/>}/><Route path="/concepts" element={<ConceptPage/>}/><Route path="/mix/:conceptId" element={<MixStudioPage/>}/><Route path="/look/:lookId" element={<FinalLookPage/>}/><Route path="*" element={<EmptyState title="Trang này chưa có trong hành trình">Khám phá một cảm hứng mới cùng AI Việt Stylist.</EmptyState>}/></Routes></div><Footer/></SessionProvider></DatabaseDataGate></ErrorBoundary>;}
