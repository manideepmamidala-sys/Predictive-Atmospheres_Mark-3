import { Component, Suspense, lazy, useLayoutEffect, useRef, type ReactNode } from 'react';
import { Link, NavLink, Navigate, Route, Routes, useLocation } from 'react-router-dom';
import { useTheme } from './design/ThemeProvider';
import { Notice } from './ui';

const Landing = lazy(() => import('./pages/Landing'));
const Study = lazy(() => import('./pages/Study'));
const Rooms = lazy(() => import('./pages/Rooms'));
const Body = lazy(() => import('./pages/Body'));
const Prediction = lazy(() => import('./pages/Prediction'));
const Studio = lazy(() => import('./pages/Studio'));
const Explore = lazy(() => import('./pages/Explore'));
const Methods = lazy(() => import('./pages/Methods'));

const pages = [
  { to: '/', label: 'Predictive Atmospheres' },
  { to: '/study', label: 'The Study' },
  { to: '/rooms', label: 'Rooms & Experience' },
  { to: '/body', label: 'Body & Experience' },
  { to: '/prediction', label: 'Prediction & Findings' },
  { to: '/studio', label: 'Design Studio' },
  { to: '/explore', label: 'Data Explorer' },
  { to: '/methods', label: 'Methods & Research Context' },
];

class PageBoundary extends Component<{ children: ReactNode }, { error: string | null }> {
  state = { error: null as string | null };
  static getDerivedStateFromError(error: Error) { return { error: error.message }; }
  render() { return this.state.error ? <Notice title="This page could not be displayed" warning><p>{this.state.error}</p><button onClick={() => this.setState({ error: null })}>Try again</button></Notice> : this.props.children; }
}

function ThemeControl() {
  const { mode, setMode } = useTheme();
  return <label className="theme-control">Appearance <select aria-label="Appearance" value={mode} onChange={event => setMode(event.target.value as typeof mode)}><option value="system">System</option><option value="light">Light</option><option value="dark">Dark</option></select></label>;
}

function OldRoute({ to, additions = {} }: { to: string; additions?: Record<string, string> }) {
  const location = useLocation();
  const query = new URLSearchParams(location.search);
  Object.entries(additions).forEach(([key, value]) => { if (!query.has(key)) query.set(key, value); });
  return <Navigate replace to={`${to}${query.size ? `?${query}` : ''}${location.hash}`} />;
}

function NotFound() {
  return <div className="not-found"><p className="eyebrow">404 · Page not found</p><h1>This room is outside the atlas.</h1><p>The address does not match a research page. Return to the study or browse the data.</p><p><Link className="action-link" to="/study">The Study <span aria-hidden="true">↗</span></Link> <Link className="action-link secondary" to="/explore">Data Explorer <span aria-hidden="true">↗</span></Link></p></div>;
}

function RoutePosition() {
  const location = useLocation();
  const previousPath = useRef<string | null>(null);
  useLayoutEffect(() => {
    const main = document.getElementById('main');
    const pathChanged = previousPath.current !== null &&
      previousPath.current !== location.pathname;
    previousPath.current = location.pathname;
    const page = pages.find(item => item.to === location.pathname);
    const pageName = page?.to === '/' ? 'Research Atlas' : page?.label ?? 'Page not found';
    document.title = `${pageName} | Predictive Atmospheres`;
    if (pathChanged) {
      window.scrollTo({ top: 0, left: 0, behavior: 'instant' });
      main?.focus({ preventScroll: true });
    }
    if (!main || !location.hash) return;

    let id: string;
    try { id = decodeURIComponent(location.hash.slice(1)); }
    catch { return; }
    let disposed = false;
    let frame = 0;
    const scrollToAnchor = () => {
      if (main.querySelector('.catalogue > p.status[role="status"]')) return false;
      const target = document.getElementById(id);
      if (!(target instanceof HTMLElement) || (target !== main && !main.contains(target))) return false;
      frame = requestAnimationFrame(() => {
        if (disposed) return;
        target.scrollIntoView({ block: 'start', behavior: 'instant' });
        if (!target.hasAttribute('tabindex')) target.tabIndex = -1;
        target.focus({ preventScroll: true });
      });
      return true;
    };
    if (scrollToAnchor()) return () => { disposed = true; cancelAnimationFrame(frame); };
    const observer = new MutationObserver(() => { if (scrollToAnchor()) observer.disconnect(); });
    observer.observe(main, { childList: true, subtree: true });
    const timeout = window.setTimeout(() => observer.disconnect(), 30_000);
    return () => { disposed = true; cancelAnimationFrame(frame); observer.disconnect(); clearTimeout(timeout); };
  }, [location.pathname, location.hash]);
  return null;
}

export default function App() {
  const location = useLocation();
  return <><RoutePosition /><a className="skip-link" href="#main">Skip to content</a><div className="site">
    <header className="site-header"><div className="header-inner"><NavLink className="brand" to="/">Predictive Atmospheres <span>Research Atlas</span></NavLink><ThemeControl /></div>
      <nav className="nav" aria-label="Research sections">{pages.map(page => <NavLink key={page.to} to={page.to} end={page.to === '/'}>{page.label}</NavLink>)}</nav></header>
    <main id="main" className="main" tabIndex={-1}><PageBoundary key={location.pathname}><Suspense fallback={<p role="status" className="page-loading">Loading page…</p>}><Routes>
      <Route path="/" element={<Landing />} /><Route path="/study" element={<Study />} /><Route path="/rooms" element={<Rooms />} /><Route path="/body" element={<Body />} /><Route path="/prediction" element={<Prediction />} /><Route path="/studio" element={<Studio />} /><Route path="/explore" element={<Explore />} /><Route path="/methods" element={<Methods />} />
      <Route path="/signals" element={<OldRoute to="/explore" additions={{ view: 'signals' }} />} /><Route path="/affect" element={<OldRoute to="/body" />} /><Route path="/people" element={<OldRoute to="/explore" additions={{ view: 'people' }} />} /><Route path="/simulator" element={<OldRoute to="/studio" />} /><Route path="/model" element={<OldRoute to="/prediction" />} />
      <Route path="*" element={<NotFound />} />
    </Routes></Suspense></PageBoundary>
      <footer className="site-footer"><span>Predictive Atmospheres · Manideep Mamidala</span><span><Link to="/methods">Methods and provenance</Link> · <a href="mailto:manideepmamidala2@gmail.com">Contact: manideepmamidala2@gmail.com</a></span></footer>
    </main>
  </div></>;
}
