import { useEffect, useState } from 'react';
import { api } from '../api';
import type { StyleProfile } from '../api';

interface Props { onNavigate: (page: any) => void; }

export default function Profiles({ onNavigate }: Props) {
  const [profiles, setProfiles] = useState<{ account: string; created_at: string; confidence: number }[]>([]);
  const [selected, setSelected] = useState<StyleProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    api.listProfiles().then(r => setProfiles(r.profiles)).catch(() => setError('تعذّر الاتصال بالخادم. تأكد من تشغيل الباك-إند.')).finally(() => setLoading(false));
  }, []);

  const openProfile = async (account: string) => {
    try { setSelected(await api.getProfile(account)); }
    catch { setError('تعذّر تحميل الملف'); }
  };

  if (selected) return <ProfileDetail profile={selected} onBack={() => setSelected(null)} />;

  return (
    <div className="page">
      <div className="page-header">
        <div className="page-eyebrow">PROFILES / الملفات</div>
        <h1 className="page-title">ملفات الأسلوب المحفوظة</h1>
        <p className="page-subtitle">الحسابات التي تم استخراج أسلوبها وتحليلها</p>
      </div>
      {error && <div className="error-box">{error}</div>}
      {loading ? (
        <div className="empty-state"><div className="loading-spin" style={{ width: 24, height: 24, margin: '0 auto' }} /></div>
      ) : profiles.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">◈</div>
          <p>لا توجد ملفات بعد. ابدأ باستخراج أسلوب حساب.</p>
          <br />
          <button className="btn btn-primary" onClick={() => onNavigate('extract')}>استخراج أسلوب جديد</button>
        </div>
      ) : (
        <>
          <div className="profile-grid">
            {profiles.map(p => (
              <div key={p.account} className="profile-card" onClick={() => openProfile(p.account)}>
                <div className="profile-card-account">@{p.account}</div>
                <div className="profile-card-meta">
                  {p.confidence > 0 && <div>ثقة: {Math.round(p.confidence * 100)}%</div>}
                  {p.created_at && <div>{new Date(p.created_at).toLocaleDateString('ar-QA')}</div>}
                </div>
              </div>
            ))}
          </div>
          <div style={{ marginTop: 24 }}><button className="btn btn-ghost" onClick={() => onNavigate('extract')}>+ إضافة ملف جديد</button></div>
        </>
      )}
    </div>
  );
}

function ScoreBar({ label, value }: { label: string; value: number }) {
  return (
    <div className="score-bar-wrap">
      <div className="score-bar-label"><span>{label}</span><span>{Math.round(value * 100)}%</span></div>
      <div className="score-bar"><div className="score-bar-fill" style={{ width: `${value * 100}%` }} /></div>
    </div>
  );
}

function Tags({ items, variant }: { items: string[]; variant?: string }) {
  if (!items?.length) return <span style={{ fontSize: 12, color: 'var(--text-dim)' }}>—</span>;
  return <div className="tag-list">{items.map((t, i) => <span key={i} className={`tag ${variant || ''}`}>{t}</span>)}</div>;
}

function ProfileDetail({ profile, onBack }: { profile: StyleProfile; onBack: () => void }) {
  return (
    <div className="page">
      <div style={{ marginBottom: 24 }}><button className="btn btn-ghost" onClick={onBack}>← رجوع</button></div>
      <div className="page-header">
        <div className="page-eyebrow">STYLE PROFILE</div>
        <h1 className="page-title">@{profile.account}</h1>
        {profile.full_name && <p className="page-subtitle">{profile.full_name}</p>}
        {profile.bio && <p className="page-subtitle" style={{ marginTop: 4, opacity: 0.7 }}>{profile.bio}</p>}
      </div>
      <div className="card">
        <div className="card-label">النبرة والمشاعر · TONE</div>
        <ScoreBar label="الرسمية" value={profile.tone.formality} />
        <div style={{ display: 'flex', gap: 12, marginTop: 12, direction: 'rtl', flexWrap: 'wrap' }}>
          <span className="badge badge-warn">{profile.tone.sentiment}</span>
          <Tags items={profile.tone.emotional_range} />
        </div>
      </div>
      <div className="grid-2">
        <div className="card">
          <div className="card-label">المفردات · VOCAB</div>
          <div style={{ marginBottom: 12 }}><div style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 6, direction: 'rtl' }}>عبارات متكررة</div><Tags items={profile.vocab.repeated_phrases} variant="accent" /></div>
          <div style={{ marginBottom: 12 }}><div style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 6, direction: 'rtl' }}>مصطلحات دينية</div><Tags items={profile.vocab.religious_terms} variant="gold" /></div>
          <div><div style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 6, direction: 'rtl' }}>الوسوم</div><Tags items={profile.vocab.hashtag_patterns} /></div>
        </div>
        <div className="card">
          <div className="card-label">القيم والمعتقدات · BELIEFS</div>
          <div style={{ marginBottom: 12 }}><div style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 6, direction: 'rtl' }}>القيم الأساسية</div><Tags items={profile.beliefs.core_values} variant="accent" /></div>
          {Object.keys(profile.beliefs.stances).length > 0 && (
            <div><div style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 6, direction: 'rtl' }}>المواقف</div>
            <table className="stances-table"><tbody>{Object.entries(profile.beliefs.stances).map(([k, v]) => <tr key={k}><td>{k}</td><td>{v}</td></tr>)}</tbody></table></div>
          )}
        </div>
      </div>
      <div className="card">
        <div className="card-label">المناطق الحساسة · RED FLAGS</div>
        <div className="grid-2">
          <div><div style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 6, direction: 'rtl' }}>مواضيع مثيرة</div><Tags items={profile.red_flags.trigger_topics} variant="danger" /></div>
          <div><div style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 6, direction: 'rtl' }}>عبارات يتجنبها</div><Tags items={profile.red_flags.avoided_phrases} variant="danger" /></div>
        </div>
      </div>
      <div style={{ fontSize: 11, color: 'var(--text-dim)', fontFamily: 'var(--font-mono)', direction: 'rtl', marginTop: 8 }}>
        النموذج: {profile.model} · {profile.created_at ? new Date(profile.created_at).toLocaleString('ar-QA') : ''}
      </div>
    </div>
  );
}
