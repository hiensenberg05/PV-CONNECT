import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Eye, EyeOff, Mail, Lock, Search, Bell, Settings, LayoutDashboard, FileText, Users, BarChart3, Calendar, Folder, Activity, TrendingUp, TrendingDown, AlertTriangle } from 'lucide-react';
const NEST20Platform = () => {
  const navigate = useNavigate();
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loginError, setLoginError] = useState('');

  // Dummy credentials
  const VALID_EMAIL = 'demo@nest.com';
  const VALID_PASSWORD = 'demo123';

  const handleLogin = (e) => {
    e.preventDefault();
    setLoginError('');

    if (email === VALID_EMAIL && password === VALID_PASSWORD) {
      navigate('/dashboard');

    } else {
      setLoginError('Invalid email or password. Try demo@nest.com / demo123');
    }
  };

  const handleLogout = () => {
    setIsLoggedIn(false);
    setEmail('');
    setPassword('');
    setLoginError('');
  };

  if (!isLoggedIn) {
    return (
      <div className="flex h-screen items-center justify-center overflow-hidden" style={{ fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, sans-serif', backgroundColor: '#e8edf2' }}>
        {/* Centered Card Container */}
        <div className="flex overflow-hidden rounded-2xl shadow-2xl" style={{ maxWidth: '900px', width: '90%', maxHeight: '90vh' }}>
          {/* Left Panel - Login Form */}
          <div className="flex flex-col justify-center px-12 py-10 bg-white" style={{ width: '45%', minWidth: '340px' }}>
            <div className="mb-10">
              <div className="flex items-center gap-2.5">
                <div className="w-9 h-9 rounded-lg flex items-center justify-center" style={{ backgroundColor: '#073d44' }}>
                  <svg fill="#ffffff" width="20" height="20" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path d="m21.743 12.331-9-10c-.379-.422-1.107-.422-1.486 0l-9 10a.998.998 0 0 0-.17 1.076c.16.361.518.593.913.593h2v7a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-7h2a.998.998 0 0 0 .743-1.669zM16 15h-3v3h-2v-3H8v-2h3v-3h2v3h3v2z" />
                  </svg>
                </div>
                <span className="text-xl font-medium" style={{ color: '#1e293b' }}>NOVA</span>
              </div>
            </div>

            <div>
              <h1 className="text-[1.75rem] font-medium mb-2 leading-tight" style={{ color: '#1e293b' }}>Welcome Back!</h1>
              <p className="mb-8 text-sm leading-relaxed" style={{ color: '#64748b' }}>
                Sign in to access your pharmacovigilance dashboard and monitor patient safety.
              </p>

              {loginError && (
                <div className="mb-5 p-3 rounded-lg text-sm" style={{ backgroundColor: '#fef2f2', border: '1px solid #fecaca', color: '#991b1b' }}>
                  {loginError}
                </div>
              )}

              <div>
                <div className="mb-4">
                  <label className="block text-sm font-medium mb-2" style={{ color: '#1e293b' }}>Email</label>
                  <div className="relative">
                    <Mail className="absolute left-3.5 top-1/2 -translate-y-1/2 w-[18px] h-[18px]" style={{ color: '#94a3b8' }} />
                    <input
                      type="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      className="w-full pl-11 pr-4 py-2.5 rounded-lg text-sm transition-all outline-none"
                      style={{ border: '1px solid #cbd5e1', color: '#1e293b' }}
                      placeholder="Enter your email"
                      onFocus={(e) => {
                        e.target.style.borderColor = '#073d44';
                        e.target.style.boxShadow = '0 0 0 1px #073d44';
                      }}
                      onBlur={(e) => {
                        e.target.style.borderColor = '#cbd5e1';
                        e.target.style.boxShadow = 'none';
                      }}
                    />
                  </div>
                </div>

                <div className="mb-2">
                  <label className="block text-sm font-medium mb-2" style={{ color: '#1e293b' }}>Password</label>
                  <div className="relative">
                    <Lock className="absolute left-3.5 top-1/2 -translate-y-1/2 w-[18px] h-[18px]" style={{ color: '#94a3b8' }} />
                    <input
                      type={showPassword ? 'text' : 'password'}
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && handleLogin(e)}
                      className="w-full pl-11 pr-11 py-2.5 rounded-lg text-sm transition-all outline-none"
                      style={{ border: '1px solid #cbd5e1', color: '#1e293b' }}
                      placeholder="Enter your password"
                      onFocus={(e) => {
                        e.target.style.borderColor = '#073d44';
                        e.target.style.boxShadow = '0 0 0 1px #073d44';
                      }}
                      onBlur={(e) => {
                        e.target.style.borderColor = '#cbd5e1';
                        e.target.style.boxShadow = 'none';
                      }}
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3.5 top-1/2 -translate-y-1/2 hover:opacity-80"
                      style={{ color: '#94a3b8' }}
                    >
                      {showPassword ? <EyeOff className="w-[18px] h-[18px]" /> : <Eye className="w-[18px] h-[18px]" />}
                    </button>
                  </div>
                </div>

                <div className="text-right mb-5">
                  <button className="text-sm font-medium hover:underline" style={{ color: '#073d44' }}>
                    Forgot Password?
                  </button>
                </div>

                <button
                  onClick={handleLogin}
                  className="w-full py-3 text-white rounded-lg font-medium text-sm transition-colors"
                  style={{ backgroundColor: '#073d44' }}
                  onMouseEnter={(e) => e.target.style.backgroundColor = '#0a5c66'}
                  onMouseLeave={(e) => e.target.style.backgroundColor = '#073d44'}
                >
                  Sign In
                </button>
              </div>

              <div className="text-center mt-5 text-sm" style={{ color: '#64748b' }}>
                Don't have an Account?{' '}
                <button className="font-medium hover:underline" style={{ color: '#073d44' }}>
                  Sign Up
                </button>
              </div>
            </div>
          </div>

          {/* Right Panel - Hero Section */}
          <div className="flex-1 px-10 py-10 flex flex-col justify-center relative overflow-hidden" style={{
            background: 'linear-gradient(to bottom right, #073d44, #0a5c66)'
          }}>
            <div className="relative z-10">
              <h2 className="text-[2rem] font-medium text-white leading-[1.2] mb-10 text-center">
                AI-Assisted Pharmacovigilance<br />For Safer Healthcare
              </h2>

              <div className="mb-12">
                <div className="text-[3rem] leading-none mb-3 font-serif text-center" style={{ color: 'rgba(255, 255, 255, 0.4)' }}>"</div>
                <p className="text-white text-base leading-relaxed mb-5 text-center italic">
                  "NOVA has transformed our adverse event reporting process. It's efficient, comprehensive, and ensures patient safety is always our top priority."
                </p>
                <div className="flex items-center gap-3 justify-center">
                  <div className="w-10 h-10 rounded-full flex items-center justify-center text-white font-medium text-sm overflow-hidden" style={{ backgroundColor: 'rgba(255, 255, 255, 0.2)' }}>
                    <img src="https://i.pravatar.cc/150?img=47" alt="DS" className="w-full h-full object-cover" />
                  </div>
                  <div>
                    <h4 className="text-white font-medium text-sm">Dr. Sarah Mitchell</h4>
                    <p className="text-xs" style={{ color: 'rgba(255, 255, 255, 0.8)' }}>Pharmacovigilance Lead at HealthCorp</p>
                  </div>
                </div>
              </div>

              <div>
                <div className="flex items-center justify-center gap-3 mb-5">
                  <div className="h-px flex-1" style={{ backgroundColor: 'rgba(255, 255, 255, 0.3)' }}></div>
                  <h3 className="text-[0.625rem] uppercase font-semibold" style={{ color: 'rgba(255, 255, 255, 0.7)', letterSpacing: '0.15em' }}>
                    TRUSTED BY HEALTHCARE LEADERS
                  </h3>
                  <div className="h-px flex-1" style={{ backgroundColor: 'rgba(255, 255, 255, 0.3)' }}></div>
                </div>
                <div className="flex flex-wrap justify-center gap-4 mb-3">
                  {[
                    { name: 'Novartis' },
                    { name: 'Pfizer' },
                    { name: 'Roche' },
                    { name: 'AstraZeneca' }
                  ].map((brand) => (
                    <div key={brand.name} className="flex items-center">
                      <span className="font-medium text-xs" style={{ color: 'rgba(255, 255, 255, 0.9)' }}>{brand.name}</span>
                    </div>
                  ))}
                </div>
                <div className="flex flex-wrap justify-center gap-4">
                  {[
                    { name: 'Merck' },
                    { name: 'GSK' },
                    { name: 'Sanofi' },
                    { name: 'Johnson & Johnson' }
                  ].map((brand) => (
                    <div key={brand.name} className="flex items-center">
                      <span className="font-medium text-xs" style={{ color: 'rgba(255, 255, 255, 0.9)' }}>{brand.name}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div >
    );
  }

};

export default NEST20Platform;