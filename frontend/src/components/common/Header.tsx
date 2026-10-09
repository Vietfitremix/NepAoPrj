import { ArrowUpRight, Menu, X } from 'lucide-react';
import { NavLink, Link, useLocation } from 'react-router-dom';
import { useEffect, useState } from 'react';
export default function Header() {
  const [open, setOpen] = useState(false); const location = useLocation();
  useEffect(() => { setOpen(false); window.scrollTo(0, 0); }, [location.pathname]);
  return <header className="site-header"><Link to="/" className="logo" aria-label="Việt Fit — Trang chủ"><img className="logo-mark" src="/emblem.png" alt=""/> VIỆT FIT<span className="logo-dot">®</span></Link><button className="mobile-menu icon-button" aria-label={open ? 'Đóng menu' : 'Mở menu'} aria-expanded={open} onClick={() => setOpen(!open)}>{open ? <X/> : <Menu/>}</button><nav className={open ? 'main-nav open' : 'main-nav'}><NavLink to="/" end>Khám phá</NavLink><NavLink to="/stylist">AI Việt Stylist <span className="mini-badge">AI</span></NavLink><NavLink to="/male-studio">Studio phối đồ</NavLink><Link to="/#how-it-works">Cách hoạt động</Link></nav><Link className="header-cta" to="/stylist">Tạo phong cách riêng <ArrowUpRight size={17}/></Link></header>;
}
