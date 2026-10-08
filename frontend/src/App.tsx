import { Component } from 'react';
import type { ReactNode } from 'react';
import { Route, Routes } from 'react-router-dom';
import { StoreProvider } from './ai/store';
import Header from './components/common/Header';
import Footer from './components/common/Footer';
import { EmptyState } from './components/common/UI';
import HomePage from './pages/HomePage';
import StylistPage from './pages/StylistPage';
import ConceptPage from './pages/ConceptPage';
import MixStudioPage from './pages/MixStudioPage';
import FinalLookPage, { SharedLookPage } from './pages/FinalLookPage';
class ErrorBoundary extends Component<{children:ReactNode},{failed:boolean}>{state={failed:false};static getDerivedStateFromError(){return {failed:true};}render(){return this.state.failed?<main className="empty-state"><h1>Chưa thể hiển thị trang này.</h1><p>Dữ liệu phiên có thể không còn tương thích. Hãy bắt đầu lại.</p><button className="button primary" onClick={()=>{try{sessionStorage.removeItem('nepao-session-v1');}catch{/* Storage may be unavailable. */}window.location.assign('/');}}>Về trang chủ</button></main>:this.props.children;}}
export default function App(){return <ErrorBoundary><StoreProvider><a href="#main-content" className="skip-link">Đến nội dung chính</a><Header/><div id="main-content"><Routes><Route path="/" element={<HomePage/>}/><Route path="/stylist" element={<StylistPage/>}/><Route path="/concepts" element={<ConceptPage/>}/><Route path="/mix" element={<MixStudioPage/>}/><Route path="/look" element={<FinalLookPage/>}/><Route path="/look/:id" element={<SharedLookPage/>}/><Route path="*" element={<EmptyState title="Trang này chưa có trong hành trình">Khám phá một cảm hứng mới cùng AI Việt Stylist.</EmptyState>}/></Routes></div><Footer/></StoreProvider></ErrorBoundary>;}
