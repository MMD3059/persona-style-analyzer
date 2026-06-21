import { useState } from 'react';
import { api } from '../api';
import type { VerificationResponse } from '../api';

export default function Verify() {
  const [account, setAccount] = useState('');
  const [text, setText] = useState('');
  const [result, setResult] = useState<VerificationResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const submit = async () => {
    if (!account.trim()) return setError('أدخل اسم الحساب');
    if (!text.trim()) return setError('أدخل النص للتحقق منه');
    setError(''); setLoading(true); setResult(null);
    try { setResult(await api.verify(account.trim(), text.trim())); }
    catch (e: any) { setError(e.message || 'حدث خطأ'); }
    finally { setLoading(false); }
  };

  const score = result ? result.similarity_score : 0;
  const scoreColor = score >= 0.7 ? 'var(--success)' : score >= 0.4 ? 'var(--warn)' : 'var(--danger)';

  return (
    <div className="page">
      <div className="page-header">
        <div className="page-eyebrow">VERIFY / تحقق</div>
        <h1 className="page-title">التحقق من الأسلوب</h1>
        <p className="page-subtitle">هل هذا النص يتوافق مع أسلوب الحساب؟</p>
      </div>
      <div className="card">
        <div className="field">
          <label>اسم الحساب</label>
          <input value={account} onChange={e => setAccount(e.target.value)} placeholder="Qatar_MOI" dir="ltr" style={{ direction: 'ltr', textAlign: 'left' }} />
        </div>
        <div className="field">
          <label>النص المراد التحقق منه</label>
          <textarea value={text} onChange={e => setText(e.target.value)} placeholder="أدخل النص هنا..." rows={5} />
        </div>
      </div>
      {error && <div className="error-box">{error}</div>}
      <button className="btn btn-primary" onClick={submit} disabled={loading}>
        {loading ? <><span className="loading-spin" /> جاري التحقق...</> : 'تحقق من الأسلوب ◎'}
      </button>
      {result && (
        <div className="result-panel">
          <div className="result-header">
            <div>
              <div style={{ fontSize: 16, fontWeight: 600, direction: 'rtl' }}>@{result.account}</div>
              <div style={{ fontSize: 12, color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>نتيجة التحقق</div>
            </div>
            <span className={`badge ${result.is_consistent ? 'badge-success' : 'badge-danger'}`}>
              {result.is_consistent ? '✓ متوافق' : '✕ غير متوافق'}
            </span>
          </div>
          <div style={{ textAlign: 'center', padding: '24px 0' }}>
            <div style={{ fontSize: 56, fontWeight: 700, color: scoreColor, fontFamily: 'var(--font-mono)', lineHeight: 1 }}>{Math.round(score * 100)}%</div>
            <div style={{ fontSize: 13, color: 'var(--text-muted)', marginTop: 8, direction: 'rtl' }}>درجة التشابه الأسلوبي</div>
          </div>
          <div className="score-bar" style={{ height: 10, borderRadius: 5 }}>
            <div className="score-bar-fill" style={{ width: `${score * 100}%`, background: `linear-gradient(90deg, ${scoreColor}88, ${scoreColor})`, height: '100%' }} />
          </div>
          {Object.keys(result.details).length > 0 && (
            <div style={{ marginTop: 20 }}>
              <div className="card-label">التفاصيل</div>
              <table className="stances-table"><tbody>
                {Object.entries(result.details).map(([k, v]) => (<tr key={k}><td>{k}</td><td>{String(v)}</td></tr>))}
              </tbody></table>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
