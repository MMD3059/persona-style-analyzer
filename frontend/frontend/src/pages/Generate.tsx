import { useState } from 'react';
import { api } from '../api';
import type { GenerationResponse } from '../api';

export default function Generate() {
  const [account, setAccount] = useState('');
  const [prompt, setPrompt] = useState('');
  const [maxTokens, setMaxTokens] = useState(500);
  const [result, setResult] = useState<GenerationResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [copied, setCopied] = useState(false);

  const submit = async () => {
    if (!account.trim()) return setError('أدخل اسم الحساب');
    if (!prompt.trim()) return setError('أدخل الموضوع أو التعليمات');
    setError(''); setLoading(true); setResult(null);
    try { setResult(await api.generate(account.trim(), prompt.trim(), maxTokens)); }
    catch (e: any) { setError(e.message || 'حدث خطأ'); }
    finally { setLoading(false); }
  };

  const copy = () => {
    if (result?.text) { navigator.clipboard.writeText(result.text); setCopied(true); setTimeout(() => setCopied(false), 2000); }
  };

  return (
    <div className="page">
      <div className="page-header">
        <div className="page-eyebrow">GENERATE / توليد</div>
        <h1 className="page-title">توليد نص بأسلوب الحساب</h1>
        <p className="page-subtitle">أنشئ محتوى يحاكي الأسلوب المستخرج للحساب</p>
      </div>
      <div className="card">
        <div className="field">
          <label>اسم الحساب</label>
          <input value={account} onChange={e => setAccount(e.target.value)} placeholder="Qatar_MOI" dir="ltr" style={{ direction: 'ltr', textAlign: 'left' }} />
        </div>
        <div className="field">
          <label>الموضوع أو التعليمات</label>
          <textarea value={prompt} onChange={e => setPrompt(e.target.value)} placeholder="مثال: اكتب تغريدة عن سلامة المرور في قطر" rows={4} />
        </div>
        <div className="field">
          <label>الحد الأقصى للرموز: {maxTokens}</label>
          <input type="range" min={100} max={1000} step={50} value={maxTokens} onChange={e => setMaxTokens(Number(e.target.value))} style={{ direction: 'ltr' }} />
        </div>
      </div>
      {error && <div className="error-box">{error}</div>}
      <button className="btn btn-primary" onClick={submit} disabled={loading}>
        {loading ? <><span className="loading-spin" /> جاري التوليد...</> : 'توليد النص ✦'}
      </button>
      {result && (
        <div className="result-panel">
          <div className="result-header">
            <div>
              <div style={{ fontSize: 16, fontWeight: 600, direction: 'rtl' }}>@{result.account}</div>
              <div style={{ fontSize: 12, color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>التزام بالأسلوب: {Math.round(result.style_adherence * 100)}%</div>
            </div>
            <button className="btn btn-ghost" onClick={copy} style={{ fontSize: 13 }}>{copied ? '✓ تم النسخ' : 'نسخ النص'}</button>
          </div>
          <div className="generated-text">{result.text}</div>
          <div style={{ marginTop: 16 }}>
            <div className="score-bar-wrap">
              <div className="score-bar-label"><span>التزام بالأسلوب</span><span>{Math.round(result.style_adherence * 100)}%</span></div>
              <div className="score-bar"><div className="score-bar-fill" style={{ width: `${result.style_adherence * 100}%` }} /></div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
