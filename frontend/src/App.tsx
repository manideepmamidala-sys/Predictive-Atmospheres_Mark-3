import { NavLink, Route, Routes } from 'react-router-dom';
import { useTheme } from './design/ThemeProvider';
import Styleguide from './design/Styleguide';
import Study from './pages/Study';
import Rooms from './pages/Rooms';
import Signals from './pages/Signals';
import Affect from './pages/Affect';
import People from './pages/People';
import Simulator from './pages/Simulator';
import ModelReport from './pages/ModelReport';

const pages = [
  { to: '/', label: 'The study' }, { to: '/rooms', label: 'Rooms' },
  { to: '/signals', label: 'Signals' }, { to: '/affect', label: 'Affect' },
  { to: '/people', label: 'People' }, { to: '/simulator', label: 'Room simulator' },
  { to: '/model', label: 'Model report' },
];
function Links({ className }: { className: string }) { return <nav className={className} aria-label="Research sections">{pages.map(({ to, label }) => <NavLink key={to} to={to} end={to === '/'}>{label}</NavLink>)}</nav>; }
function ThemeControl() {
  const { mode, setMode } = useTheme();
  return <div className="theme-control"><label>Appearance<select aria-label="Appearance" value={mode} onChange={event => setMode(event.target.value as typeof mode)}><option value="system">System</option><option value="light">Light</option><option value="dark">Dark</option></select></label></div>;
}
export default function App() {
  return <><a className="skip-link" href="#main">Skip to content</a><div className="site">
    <aside className="rail"><NavLink className="brand" to="/">Predictive Atmospheres<small>A research atlas</small></NavLink><Links className="nav" /><ThemeControl /></aside>
    <div><div className="mobile-header"><NavLink className="brand" to="/">Predictive Atmospheres<small>A research atlas</small></NavLink><ThemeControl /></div><Links className="mobile-nav" />
      <main id="main" className="main" tabIndex={-1}><Routes><Route path="/" element={<Study />} /><Route path="/rooms" element={<Rooms />} /><Route path="/signals" element={<Signals />} /><Route path="/affect" element={<Affect />} /><Route path="/people" element={<People />} /><Route path="/simulator" element={<Simulator />} /><Route path="/model" element={<ModelReport />} /><Route path="/styleguide" element={<Styleguide />} /></Routes>
        <footer className="site-footer">Predictive Atmospheres · Pilot research platform · Methods, missingness and model limits are part of the evidence.</footer></main></div></div></>;
}
