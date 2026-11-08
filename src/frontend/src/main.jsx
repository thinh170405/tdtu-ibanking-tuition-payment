import React, { useEffect, useRef, useState } from 'react';
import { createRoot } from 'react-dom/client';
import './style.css';

const accountBase = import.meta.env.VITE_ACCOUNT_API_BASE_URL || 'http://localhost:8081/api/v1';
const paymentBase = import.meta.env.VITE_PAYMENT_API_BASE_URL || 'http://localhost:8082/api/v1';
const money = (n) =>
  new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(n || 0);
const statusLabel = (status) =>
  ({ SUCCESS: 'Thành công', PENDING_OTP: 'Chờ OTP', FAILED: 'Thất bại', EXPIRED: 'Hết hạn' })[
    status
  ] || status;

async function api(base, path, token, options = {}) {
  const response = await fetch(base + path, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(options.headers || {}),
    },
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok)
    throw Object.assign(new Error(data.message || 'Không thể kết nối máy chủ.'), {
      code: data.code,
      status: response.status,
    });
  return data;
}

function Dashboard({ profile, wallet, history, onPayment, onLogout }) {
  const successful = history.filter((item) => item.status === 'SUCCESS');
  return (
    <div className="shell dashboard-page">
      <header>
        <div className="brand">
          i<span>Banking</span>
        </div>
        <nav className="app-nav" aria-label="Điều hướng chính">
          <span className="current">Tổng quan</span>
          <button className="nav-link" onClick={onPayment}>
            Đóng học phí
          </button>
        </nav>
        <div className="header-actions">
          <span>{profile?.fullName || 'Đang tải…'}</span>
          <button className="link-button" onClick={onLogout}>
            Đăng xuất
          </button>
        </div>
      </header>
      <main className="content dashboard-content">
        <div className="dashboard-intro">
          <span className="eyebrow">TỔNG QUAN TÀI KHOẢN</span>
          <h1>Xin chào, {profile?.fullName || 'bạn'}.</h1>
          <p>Quản lý số dư và thực hiện thanh toán học phí từ một nơi.</p>
        </div>
        <div className="dashboard-grid">
          <section className="dashboard-balance">
            <span>SỐ DƯ KHẢ DỤNG</span>
            <strong>{wallet ? money(wallet.balance) : '—'}</strong>
            <small>Tài khoản thanh toán · VND</small>
          </section>
          <section className="card dashboard-action">
            <span className="eyebrow">DỊCH VỤ TRỰC TUYẾN</span>
            <h2>Đóng học phí TDTU</h2>
            <p>Tra cứu khoản học phí theo MSSV và xác nhận giao dịch bằng OTP qua email.</p>
            <button onClick={onPayment}>
              Đến trang thanh toán <span aria-hidden="true">→</span>
            </button>
          </section>
        </div>
        <div className="dashboard-grid dashboard-lower">
          <section className="card">
            <h2>Thông tin tài khoản</h2>
            <div className="account-list">
              <div>
                <span>Họ và tên</span>
                <strong>{profile?.fullName || '—'}</strong>
              </div>
              <div>
                <span>Số điện thoại</span>
                <strong>{profile?.phone || '—'}</strong>
              </div>
              <div>
                <span>Email</span>
                <strong>{profile?.email || '—'}</strong>
              </div>
            </div>
          </section>
          <section className="card">
            <h2>Giao dịch gần đây</h2>
            {history.length ? (
              <>
                <div className="recent-payment">
                  <div>
                    <strong>{history[0].studentName}</strong>
                    <span>
                      {history[0].studentId} · {statusLabel(history[0].status)}
                    </span>
                  </div>
                  <b>{money(history[0].amount)}</b>
                </div>
                <p className="hint">{successful.length} giao dịch đã thanh toán thành công.</p>
              </>
            ) : (
              <p className="hint">Chưa có giao dịch học phí.</p>
            )}
          </section>
        </div>
      </main>
    </div>
  );
}

function App() {
  const [page, setPage] = useState(window.location.pathname);
  const [token, setToken] = useState(sessionStorage.getItem('token') || '');
  const [username, setUsername] = useState('demo3');
  const [password, setPassword] = useState('Demo!2026');
  const [profile, setProfile] = useState(null);
  const [wallet, setWallet] = useState(null);
  const [history, setHistory] = useState([]);
  const [mssv, setMssv] = useState('');
  const [tuition, setTuition] = useState(null);
  const [payment, setPayment] = useState(null);
  const [otp, setOtp] = useState('');
  const [terms, setTerms] = useState(false);
  const [busy, setBusy] = useState(false);
  const [lookingUp, setLookingUp] = useState(false);
  const [notice, setNotice] = useState(null);
  const lookupSeq = useRef(0);
  const requestId = useRef(null);
  useEffect(() => {
    const onPop = () => setPage(window.location.pathname);
    window.addEventListener('popstate', onPop);
    return () => window.removeEventListener('popstate', onPop);
  }, []);
  const navigate = (path) => {
    window.history.pushState({}, '', path);
    setPage(path);
    setNotice(null);
    window.scrollTo(0, 0);
  };

  const message = (text, kind = 'error') => setNotice({ text, kind });
  const refresh = async (current) => {
    const [p, w, h] = await Promise.all([
      api(accountBase, '/users/me', current),
      api(paymentBase, '/wallet', current),
      api(paymentBase, '/payments', current),
    ]);
    setProfile(p);
    setWallet(w);
    setHistory(h.items || []);
  };
  useEffect(() => {
    if (!token) return;
    refresh(token).catch((e) => {
      message(e.message);
      if (e.status === 401) logout();
    });
  }, [token]);
  const logout = () => {
    sessionStorage.removeItem('token');
    setToken('');
    setProfile(null);
    setWallet(null);
    setHistory([]);
    setTuition(null);
    setPayment(null);
  };
  const login = async (e) => {
    e.preventDefault();
    setBusy(true);
    setNotice(null);
    try {
      const result = await api(accountBase, '/auth/login', null, {
        method: 'POST',
        body: JSON.stringify({ username, password }),
      });
      sessionStorage.setItem('token', result.accessToken);
      setToken(result.accessToken);
    } catch (e) {
      message(e.message);
    } finally {
      setBusy(false);
    }
  };
  useEffect(() => {
    const seq = ++lookupSeq.current;
    setTuition(null);
    setPayment(null);
    setTerms(false);
    setOtp('');
    requestId.current = null;
    if (!token || !/^\d{8}$/.test(mssv)) {
      setLookingUp(false);
      return;
    }
    const controller = new AbortController();
    setLookingUp(true);
    setNotice(null);
    const timer = setTimeout(
      () =>
        api(paymentBase, `/tuition/${mssv}`, token, { signal: controller.signal })
          .then((data) => {
            if (seq === lookupSeq.current) setTuition(data);
          })
          .catch((e) => {
            if (e.name !== 'AbortError' && seq === lookupSeq.current) message(e.message);
          })
          .finally(() => {
            if (seq === lookupSeq.current) setLookingUp(false);
          }),
      300,
    );
    return () => {
      clearTimeout(timer);
      controller.abort();
    };
  }, [mssv, token]);
  const createPayment = async () => {
    if (!tuition || !terms || busy) return;
    requestId.current ||= crypto.randomUUID();
    setBusy(true);
    setNotice(null);
    try {
      const p = await api(paymentBase, '/payments', token, {
        method: 'POST',
        body: JSON.stringify({
          tuitionId: tuition.tuitionId,
          termsAccepted: true,
          requestId: requestId.current,
        }),
      });
      setPayment(p);
      message('OTP đã được gửi đến email của người nộp.', 'success');
    } catch (e) {
      message(e.message);
      if (e.code !== 'REQUEST_IN_PROGRESS') requestId.current = null;
    } finally {
      setBusy(false);
    }
  };
  const confirm = async (e) => {
    e.preventDefault();
    if (!payment || busy) return;
    setBusy(true);
    setNotice(null);
    try {
      const p = await api(paymentBase, `/payments/${payment.paymentId}/confirm`, token, {
        method: 'POST',
        body: JSON.stringify({ otp }),
      });
      setPayment(p);
      await refresh(token);
      setTuition((t) => (t ? { ...t, status: 'PAID', paidAt: p.paidAt } : t));
      message('Thanh toán học phí thành công.', 'success');
    } catch (e) {
      message(e.message);
      if (['OTP_EXPIRED', 'TUITION_ALREADY_PAID', 'INSUFFICIENT_BALANCE'].includes(e.code)) {
        const p = await api(paymentBase, `/payments/${payment.paymentId}`, token).catch(() => null);
        if (p) setPayment(p);
      }
    } finally {
      setBusy(false);
    }
  };

  if (!token)
    return (
      <main className="login-page">
        <form className="card login" onSubmit={login}>
          <div className="brand">
            i<span>Banking</span>
          </div>
          <h1>Đăng nhập iBanking</h1>
          <p>Truy cập tài khoản và dịch vụ đóng học phí.</p>
          <label>
            Tên đăng nhập
            <input value={username} onChange={(e) => setUsername(e.target.value)} required />
          </label>
          <label>
            Mật khẩu
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </label>
          {notice && <div className={`notice ${notice.kind}`}>{notice.text}</div>}
          <button disabled={busy}>{busy ? 'Đang đăng nhập…' : 'Đăng nhập'}</button>
        </form>
      </main>
    );
  if (page !== '/tuition-payment')
    return (
      <Dashboard
        profile={profile}
        wallet={wallet}
        history={history}
        onPayment={() => navigate('/tuition-payment')}
        onLogout={logout}
      />
    );
  return (
    <div className="shell">
      <header>
        <div className="brand">
          i<span>Banking</span>
        </div>
        <nav className="app-nav" aria-label="Điều hướng chính">
          <button className="nav-link" onClick={() => navigate('/')}>
            Tổng quan
          </button>
          <span className="current">Đóng học phí</span>
        </nav>
        <div className="header-actions">
          <span>{profile?.fullName || 'Đang tải…'}</span>
          <button className="link-button" onClick={logout}>
            Đăng xuất
          </button>
        </div>
      </header>
      <main className="content">
        <div className="title">
          <div>
            <span className="eyebrow">DỊCH VỤ HỌC PHÍ</span>
            <h1>Thanh toán học phí</h1>
            <p>Tra cứu khoản cần đóng và xác nhận bằng OTP qua email.</p>
          </div>
          <div className="balance">
            <small>Số dư khả dụng</small>
            <strong>{wallet ? money(wallet.balance) : '—'}</strong>
          </div>
        </div>
        {notice && <div className={`notice ${notice.kind}`}>{notice.text}</div>}
        <div className="grid">
          <section className="card">
            <h2>1. Người nộp tiền</h2>
            <div className="fields">
              <div>
                <small>Họ và tên</small>
                <b>{profile?.fullName || '—'}</b>
              </div>
              <div>
                <small>Số điện thoại</small>
                <b>{profile?.phone || '—'}</b>
              </div>
              <div>
                <small>Email</small>
                <b>{profile?.email || '—'}</b>
              </div>
              <div>
                <small>Số dư tài khoản</small>
                <b>{wallet ? money(wallet.balance) : '—'}</b>
              </div>
            </div>
          </section>
          <section className="card">
            <h2>2. Tra cứu học phí</h2>
            <label>
              Mã số sinh viên
              <input
                inputMode="numeric"
                maxLength={8}
                placeholder="Nhập 8 chữ số"
                value={mssv}
                onChange={(e) => setMssv(e.target.value.replace(/\D/g, ''))}
              />
            </label>
            {lookingUp && <p className="hint">Đang tra cứu…</p>}
            {tuition && (
              <div className="tuition">
                <div>
                  <span>Sinh viên</span>
                  <strong>{tuition.studentName}</strong>
                </div>
                <div>
                  <span>MSSV</span>
                  <strong>{tuition.studentId}</strong>
                </div>
                <div>
                  <span>Mã học phí</span>
                  <strong>{tuition.tuitionId}</strong>
                </div>
                <div>
                  <span>Trạng thái</span>
                  <strong>{tuition.status === 'PAID' ? 'Đã thanh toán' : 'Chưa thanh toán'}</strong>
                </div>
                <div className="amount">
                  <span>Số tiền học phí</span>
                  <strong>{money(tuition.amount)}</strong>
                </div>
              </div>
            )}
            {tuition?.status === 'UNPAID' && !payment && (
              <>
                <div className="terms">
                  <strong>Điều khoản thanh toán</strong>
                  <p>
                    Bạn xác nhận thanh toán toàn bộ khoản học phí hiển thị bằng tài khoản đang đăng
                    nhập. Hệ thống chỉ ghi nợ sau khi OTP hợp lệ; kết quả và lịch sử giao dịch được
                    lưu để đối chiếu.
                  </p>
                </div>
                <label className="check">
                  <input
                    type="checkbox"
                    checked={terms}
                    onChange={(e) => setTerms(e.target.checked)}
                  />{' '}
                  Tôi đã đọc và đồng ý với điều khoản thanh toán trên.
                </label>
                <button
                  disabled={busy || !terms || !wallet || wallet.balance < tuition.amount}
                  onClick={createPayment}
                >
                  {busy ? 'Đang xử lý…' : 'Xác nhận thanh toán toàn bộ'}
                </button>
                {wallet && wallet.balance < tuition.amount && (
                  <p className="hint error-text">Số dư không đủ để thanh toán.</p>
                )}
              </>
            )}
          </section>
        </div>
        {payment && (
          <section className="card otp-card">
            <h2>3. Xác thực giao dịch</h2>
            <p>
              Giao dịch <b>{payment.paymentId}</b> · {money(payment.amount)}
            </p>
            {payment.status === 'PENDING_OTP' ? (
              <form onSubmit={confirm}>
                <label>
                  Mã OTP gồm 6 chữ số
                  <input
                    inputMode="numeric"
                    maxLength={6}
                    value={otp}
                    onChange={(e) => setOtp(e.target.value.replace(/\D/g, ''))}
                    placeholder="Nhập OTP từ email"
                    required
                  />
                </label>
                <p className="hint">
                  Hạn OTP: {new Date(payment.otpExpiresAt).toLocaleString('vi-VN')}
                </p>
                <button disabled={busy || !/^\d{6}$/.test(otp)}>
                  {busy ? 'Đang xác nhận…' : 'Hoàn tất thanh toán'}
                </button>
              </form>
            ) : (
              <p className="result">
                {payment.status === 'SUCCESS'
                  ? 'Thanh toán thành công'
                  : `Giao dịch ${payment.status}`}
              </p>
            )}
          </section>
        )}
        <section className="card history">
          <h2>Lịch sử giao dịch</h2>
          {history.length ? (
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Giao dịch</th>
                    <th>Sinh viên</th>
                    <th>Số tiền</th>
                    <th>Trạng thái</th>
                  </tr>
                </thead>
                <tbody>
                  {history.map((p) => (
                    <tr key={p.paymentId}>
                      <td>{p.paymentId}</td>
                      <td>
                        {p.studentName}
                        <br />
                        <small>{p.studentId}</small>
                      </td>
                      <td>{money(p.amount)}</td>
                      <td>{statusLabel(p.status)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p className="hint">Chưa có giao dịch.</p>
          )}
        </section>
      </main>
    </div>
  );
}

createRoot(document.getElementById('root')).render(<App />);
