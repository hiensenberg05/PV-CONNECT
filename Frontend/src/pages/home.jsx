import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Eye, EyeOff, User, Lock, Activity, FileText, BarChart3, AlertTriangle } from 'lucide-react';
import toast, { Toaster } from 'react-hot-toast';
import { login } from '../api/auth';

const NEST20Platform = () => {
  const navigate = useNavigate();
  const [employeeId, setEmployeeId] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loginError, setLoginError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoginError('');
    setIsLoading(true);

    try {
      // Call backend login API
      await login(employeeId, password);

      // Show success toast
      toast.success('Login successful! Redirecting...', {
        duration: 2000,
        style: {
          background: '#073d44',
          color: '#fff',
        },
        iconTheme: {
          primary: '#7dd3fc',
          secondary: '#073d44',
        },
      });

      // Navigate to dashboard after short delay
      setTimeout(() => {
        navigate('/dashboard');
      }, 1000);

    } catch (error) {
      // Handle error with inline message
      if (error.response?.status === 401) {
        setLoginError('Invalid Employee ID or password. Please try again.');
        toast.error('Invalid credentials', {
          duration: 3000,
        });
      } else if (error.response?.data?.detail) {
        setLoginError(error.response.data.detail);
        toast.error(error.response.data.detail, {
          duration: 3000,
        });
      } else {
        setLoginError('An error occurred. Please check your connection and try again.');
        toast.error('Connection error. Please try again.', {
          duration: 3000,
        });
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4" style={{ background: 'linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%)' }}>
      {/* Toast Container */}
      <Toaster position="top-center" reverseOrder={false} />

      {/* Centered Card Container */}
      <div className="w-full max-w-4xl rounded-2xl shadow-2xl overflow-hidden flex" style={{ backgroundColor: '#ffffff', minHeight: '600px' }}>

        {/* Left Panel - Login Form */}
        <div className="w-full lg:w-1/2 p-12 flex flex-col justify-center">
          <div className="mb-8">
            <h2 className="text-3xl font-bold mb-2" style={{ color: '#073d44' }}>
              NOVA
            </h2>
            <h3 className="text-2xl font-semibold mb-2" style={{ color: '#1e293b' }}>
              Welcome Back!
            </h3>
            <p className="text-sm" style={{ color: '#64748b' }}>
              Sign in with your Employee ID to access the pharmacovigilance dashboard.
            </p>
          </div>

          {loginError && (
            <div className="mb-6 p-3 rounded-lg" style={{ backgroundColor: '#fee2e2', border: '1px solid #fecaca' }}>
              <p className="text-sm" style={{ color: '#dc2626' }}>{loginError}</p>
            </div>
          )}

          <form onSubmit={handleLogin}>
            <div className="mb-5">
              <label className="block text-sm font-medium mb-2" style={{ color: '#334155' }}>
                Employee ID
              </label>
              <div className="relative">
                <User className="absolute left-3.5 top-1/2 -translate-y-1/2" size={18} style={{ color: '#94a3b8' }} />
                <input
                  type="text"
                  required
                  value={employeeId}
                  onChange={(e) => setEmployeeId(e.target.value.toUpperCase())}
                  className="w-full pl-11 pr-4 py-2.5 rounded-lg text-sm transition-all outline-none"
                  style={{ border: '1px solid #cbd5e1', color: '#1e293b' }}
                  placeholder="Enter your Employee ID "
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

            <div className="mb-5">
              <label className="block text-sm font-medium mb-2" style={{ color: '#334155' }}>
                Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3.5 top-1/2 -translate-y-1/2" size={18} style={{ color: '#94a3b8' }} />
                <input
                  type={showPassword ? 'text' : 'password'}
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
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
                  {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full py-3 rounded-lg font-semibold text-white transition-all"
              style={{
                backgroundColor: isLoading ? '#94a3b8' : '#073d44',
                cursor: isLoading ? 'not-allowed' : 'pointer'
              }}
              onMouseEnter={(e) => !isLoading && (e.target.style.backgroundColor = '#0a5c66')}
              onMouseLeave={(e) => !isLoading && (e.target.style.backgroundColor = '#073d44')}
            >
              {isLoading ? 'Signing In...' : 'Sign In'}
            </button>
          </form>
        </div>

        {/* Right Panel - Hero Section */}
        <div className="hidden lg:flex w-1/2 relative overflow-hidden" style={{ backgroundColor: '#0a5860' }}>
          {/* Content */}
          <div className="relative z-10 flex flex-col justify-center px-16 text-white">
            {/* Main Heading */}
            <div className="mb-10">
              <h1 className="text-4xl font-bold leading-tight mb-6">
                AI-Assisted<br />
                Pharmacovigilance
              </h1>
              <div className="w-16 h-1 mb-6" style={{ backgroundColor: '#7dd3fc' }}></div>
              <p className="text-base leading-relaxed" style={{ color: '#e0f2fe' }}>
                Monitor adverse events, ensure regulatory compliance, and protect patient safety with intelligent automation.
              </p>
            </div>

            {/* Key Features */}
            <div className="space-y-6">
              <div className="flex items-start">
                <div className="mr-4 mt-1">
                  <Activity size={24} style={{ color: '#7dd3fc' }} />
                </div>
                <div>
                  <h3 className="font-semibold text-lg mb-1">Real-Time Monitoring</h3>
                  <p className="text-sm" style={{ color: '#cbd5e1' }}>Track adverse events as they happen</p>
                </div>
              </div>

              <div className="flex items-start">
                <div className="mr-4 mt-1">
                  <FileText size={24} style={{ color: '#7dd3fc' }} />
                </div>
                <div>
                  <h3 className="font-semibold text-lg mb-1">Automated Reporting</h3>
                  <p className="text-sm" style={{ color: '#cbd5e1' }}>Generate compliance-ready documentation</p>
                </div>
              </div>

              <div className="flex items-start">
                <div className="mr-4 mt-1">
                  <BarChart3 size={24} style={{ color: '#7dd3fc' }} />
                </div>
                <div>
                  <h3 className="font-semibold text-lg mb-1">Advanced Analytics</h3>
                  <p className="text-sm" style={{ color: '#cbd5e1' }}>Identify trends and patterns instantly</p>
                </div>
              </div>

              <div className="flex items-start">
                <div className="mr-4 mt-1">
                  <AlertTriangle size={24} style={{ color: '#7dd3fc' }} />
                </div>
                <div>
                  <h3 className="font-semibold text-lg mb-1">Smart Alerts</h3>
                  <p className="text-sm" style={{ color: '#cbd5e1' }}>Get notified of critical safety signals</p>
                </div>
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
};

export default NEST20Platform;