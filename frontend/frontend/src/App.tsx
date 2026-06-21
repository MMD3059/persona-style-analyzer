import { useState } from 'react';
import Extract from './pages/Extract';
import Verify from './pages/Verify';
import Generate from './pages/Generate';
import Profiles from './pages/Profiles';
import './App.css';

type Page = 'profiles' | 'extract' | 'verify' | 'generate';

const NAV = [
  { id: 'profiles' as Page, label: 'الملفات', labelEn: 'Profiles', icon: '◈' },
  { id: 'extract' as Page, label: 'استخراج', labelEn: 'Extract', icon: '⬡' },
  { id: 'verify' as Page, label: 'تحقق', labelEn: 'Verify', icon: '◎' },
  { id: 'generate' as Page, label: 'توليد', labelEn: 'Generate', icon: '✦' },
];

export default function App() {
  const [page, setPage] = useState<Page>('profiles');

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="sidebar-brand">
          <div className="brand-mark">م</div>
          <div className="brand-text">
            <span className="brand-ar">محلل الأسلوب</span>
            <span className="brand-en">Persona Analyzer</span>
          </div>
        </div>
        <nav className="sidebar-nav">
          {NAV.map(n => (
            <button
              key={n.id}
              className={"nav-item" + (page === n.id ? " active" : "")}
              onClick={() => setPage(n.id)}
            >
              <span className="nav-icon">{n.icon}</span>
              <span className="nav-labels">
                <span className="nav-ar">{n.label}</span>
                <span className="nav-en">{n.labelEn}</span>
              </span>
              {page === n.id && <span className="nav-pip" />}
            </button>
          ))}
        </nav>
        <div className="sidebar-footer">
          <div className="api-status">
            <span className="status-dot" />
            <span>Fanar LLM</span>
          </div>
        </div>
      </aside>
      <main className="main-content">
        {page === 'profiles' && <Profiles onNavigate={setPage} />}
        {page === 'extract' && <Extract />}
        {page === 'verify' && <Verify />}
        {page === 'generate' && <Generate />}
      </main>
    </div>
  );
}
