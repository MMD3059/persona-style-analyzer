import { useState } from 'react';
import { api } from '../api';
import type { ExtractionResponse, Tweet } from '../api';

interface TweetRow { id: string; content: string; }
let counter = 1;
const newRow = (): TweetRow => ({ id: String(counter++), content: '' });

export default function Extract() {
  const [account, setAccount] = useState('');
  const [fullName, setFullName] = useState('');
  const [bio, setBio] = useState('');
  const [tweets, setTweets] = useState<TweetRow[]>([newRow(), newRow(), newRow()]);
  const [result, setResult] = useState<ExtractionResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const updateTweet = (id: string, content: string) =>
    setTweets(t => t.map(r => r.id === id ? { ...r, content } : r));
  const removeTweet = (id: string) => setTweets(t => t.filter(r => r.id !== id));
  const addTweet = () => setTweets(t => [...t, newRow()]);

  const submit = async () => {
    if (!account.trim()) return setError('أدخل اسم الحساب');
    const filled = tweets.filter(t => t.content.trim());
    if (filled.length === 0) return setError('أضف تغريدة واحدة على الأقل');
    setError(''); setLoading(true); setResult(null);
    try {
      const payload: Tweet[] = filled.map(t => ({ id: t.id, account: account.trim(), content: t.content.trim() }));
      setResult(await api.extract(account.trim(), payload, fullName || undefined, bio || undefined));
    } catch (e: any) {
      setError(e.message || 'حدث خطأ');
    } finally { setLoading(false); }
  };

  return (
    <div className="page">
      <div className="page-header">
        <div className="page-eyebrow">EXTRACT / استخراج</div>
        <h1 className="page-title">استخراج الأسلوب</h1>
        <p className="page-subtitle">أدخل تغريدات الحساب لاستخراج ملف أسلوبه اللغوي</p>
      </div>
      <div className="card">
        <div className="card-label">معلومات الحساب</div>
        <div className="grid-2">
          <div className="field">
            <label>اسم الحساب *</label>
            <input value={account} onChange={e => setAccount(e.target.value)} placeholder="Qatar_MOI" dir="ltr" style={{ direction: 'ltr', textAlign: 'left' }} />
          </div>
          <div className="field">
            <label>الاسم الكامل (اختياري)</label>
            <input value={fullName} onChange={e => setFullName(e.target.value)} placeholder="وزارة الداخلية" />
          </div>
        </div>
        <div className="field">
          <label>النبذة الشخصية (اختياري)</label>
          <input value={bio} onChange={e => setBio(e.target.value)} placeholder="نبذة مختصرة عن الحساب" />
        </div>
      </div>
      <div className="card">
        <div className="card-label">التغريدات · {tweets.length} تغريدة</div>
        <div className="rows-editor">
          {tweets.map(t => (
            <div className="tweet-row" key={t.id}>
              <textarea style={{ flex: 1, background: 'var(--surface2)', border: '1px solid var(--border)', borderRadius: 'var(--radius)', padding: '10px 14px', color: 'var(--text)', fontSize: 14, outline: 'none', minHeight: 60, resize: 'vertical', direction: 'rtl', fontFamily: 'var(--font-ar)' }} placeholder="أدخل نص التغريدة..." value={t.content} onChange={e => updateTweet(t.id, e.target.value)} />
              {tweets.length > 1 && <button className="remove-btn" onClick={() => removeTweet(t.id)}>✕</button>}
            </div>
          ))}
        </div>
        <div style={{ marginTop: 12 }}>
          <button className="btn btn-ghost" onClick={addTweet}>+ إضافة تغريدة</button>
        </div>
      </div>
      {error && <div className="error-box">{error}</div>}
      <button className="btn btn-primary" onClick={submit} disabled={loading}>
        {loading ? <><span className="loading-spin" /> جاري الاستخراج...</> : 'استخراج الأسلوب ⬡'}
      </button>
      {result && (
        <div className="result-panel">
          <div className="result-header">
            <div>
              <div style={{ fontSize: 18, fontWeight: 700, direction: 'rtl' }}>@{result.profile.account}</div>
              <div style={{ fontSize: 12, color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>{result.tweet_count} تغريدة · ثقة: {Math.round(result.confidence * 100)}%</div>
            </div>
            <span className="badge badge-success">✓ تم الاستخراج</span>
          </div>
          <div className="score-bar-wrap">
            <div className="score-bar-label"><span>مستوى الثقة</span><span>{Math.round(result.confidence * 100)}%</span></div>
            <div className="score-bar"><div className="score-bar-fill" style={{ width: `${result.confidence * 100}%` }} /></div>
          </div>
          <hr className="section-divider" />
          <div style={{ marginBottom: 16 }}>
            <div className="card-label">المفردات المميزة</div>
            <div className="tag-list">
              {result.profile.vocab.repeated_phrases.map((p: string, i: number) => <span key={i} className="tag accent">{p}</span>)}
              {result.profile.vocab.religious_terms.map((p: string, i: number) => <span key={i} className="tag gold">{p}</span>)}
            </div>
          </div>
          <div>
            <div className="card-label">القيم الأساسية</div>
            <div className="tag-list">{result.profile.beliefs.core_values.map((v: string, i: number) => <span key={i} className="tag">{v}</span>)}</div>
          </div>
        </div>
      )}
    </div>
  );
}
