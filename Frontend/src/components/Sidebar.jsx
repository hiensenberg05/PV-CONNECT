import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, ChevronDown, LogOut, Bell, LayoutDashboard, FileText, BarChart3, Zap, Database, Building2, Users, Settings, HelpCircle, Activity, Shield, Pill, User } from 'lucide-react';
import useThemeStore from '../store/themeStore';

const Sidebar = ({ activeView = 'dashboard', onViewChange }) => {
    const { darkMode } = useThemeStore();
    const navigate = useNavigate();

    const handleNavClick = (view) => {
        if (onViewChange) {
            onViewChange(view);
        }
    };

    const isActive = (view) => activeView === view;

    const getNavItemStyle = (view) => {
        if (isActive(view)) {
            return {
                backgroundColor: '#073d44',
                color: '#ffffff'
            };
        }
        return {
            color: darkMode ? '#d1d5db' : '#4b5563',
            backgroundColor: 'transparent'
        };
    };

    return (
        <aside className="w-56 flex flex-col" style={{
            backgroundColor: darkMode ? '#111827' : '#ffffff',
            borderRight: `1px solid ${darkMode ? '#374151' : '#e5e7eb'}`,
            transition: 'all 0.3s ease'
        }}>
            {/* Logo */}
            <div className="px-4 py-4">
                <div className="flex items-center gap-2">
                    <div className="w-7 h-7 rounded-md flex items-center justify-center" style={{ backgroundColor: '#073d44' }}>
                        <svg fill="#ffffff" width="16" height="16" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                            <path d="m21.743 12.331-9-10c-.379-.422-1.107-.422-1.486 0l-9 10a.998.998 0 0 0-.17 1.076c.16.361.518.593.913.593h2v7a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-7h2a.998.998 0 0 0 .743-1.669zM16 15h-3v3h-2v-3H8v-2h3v-3h2v3h3v2z" />
                        </svg>
                    </div>
                    <div>
                        <div className="text-sm font-semibold" style={{ color: darkMode ? '#f9fafb' : '#111827' }}>NOVA</div>
                        <div className="text-xs" style={{ color: darkMode ? '#9ca3af' : '#6b7280' }}>Pharmacovigilance</div>
                    </div>
                    <ChevronDown className="w-4 h-4 ml-auto" style={{ color: darkMode ? '#9ca3af' : '#9ca3af' }} />
                </div>
            </div>

            {/* Search
            <div className="px-4 pb-3">
                <div className="relative">
                    <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 w-4 h-4" style={{ color: darkMode ? '#9ca3af' : '#9ca3af' }} />
                    <input
                        type="text"
                        placeholder="Search..."
                        className="w-full pl-8 pr-8 py-1.5 text-sm rounded-md outline-none"
                        style={{
                            backgroundColor: darkMode ? '#374151' : '#f3f4f6',
                            border: `1px solid ${darkMode ? '#4b5563' : '#e5e7eb'}`,
                            color: darkMode ? '#f9fafb' : '#111827'
                        }}
                    />
                    <kbd className="absolute right-2 top-1/2 -translate-y-1/2 px-1.5 py-0.5 text-xs font-medium rounded" style={{
                        color: darkMode ? '#9ca3af' : '#6b7280',
                        backgroundColor: darkMode ? '#1f2937' : '#ffffff',
                        border: `1px solid ${darkMode ? '#4b5563' : '#e5e7eb'}`
                    }}>⌘K</kbd>
                </div>
            </div> */}

            {/* Main Navigation */}
            <nav className="flex-1 px-2 overflow-y-auto">
                <div className="space-y-0.5">
                    {/* Dashboard */}
                    <div
                        onClick={() => handleNavClick('dashboard')}
                        className="flex items-center gap-2 px-2 py-1.5 rounded-md text-sm font-medium cursor-pointer transition-colors"
                        style={getNavItemStyle('dashboard')}
                    >
                        <LayoutDashboard className="w-4 h-4" />
                        <span>Dashboard</span>
                    </div>

                    {/* Alerts */}
                    <div
                        className="flex items-center justify-between gap-2 px-2 py-1.5 rounded-md text-sm font-medium cursor-pointer"
                        style={{ color: darkMode ? '#d1d5db' : '#4b5563' }}
                        onMouseEnter={(e) => e.currentTarget.style.backgroundColor = darkMode ? '#374151' : '#f3f4f6'}
                        onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
                    >
                        <div className="flex items-center gap-2">
                            <Bell className="w-4 h-4" />
                            <span>Alerts</span>
                        </div>
                        <span className="px-1.5 py-0.5 text-xs font-semibold text-white rounded" style={{ backgroundColor: '#073d44' }}>8</span>
                    </div>

                    {/* Other nav items */}
                    {['Case Reports', 'Signal Detection', 'Safety Reports', 'Analytics', 'AI Insights'].map((item, idx) => {
                        const icons = [FileText, Activity, Shield, BarChart3, Zap];
                        const Icon = icons[idx];
                        const viewKeys = { 'Analytics': 'analytics', 'Signal Detection': 'signals' };
                        const viewKey = viewKeys[item] || null;
                        const isClickable = viewKey !== null;

                        return (
                            <div
                                key={item}
                                onClick={() => isClickable && handleNavClick(viewKey)}
                                className="flex items-center gap-2 px-2 py-1.5 rounded-md text-sm font-medium cursor-pointer transition-colors"
                                style={isClickable ? getNavItemStyle(viewKey) : { color: darkMode ? '#d1d5db' : '#4b5563' }}
                                onMouseEnter={(e) => !isActive(viewKey) && (e.currentTarget.style.backgroundColor = darkMode ? '#374151' : '#f3f4f6')}
                                onMouseLeave={(e) => !isActive(viewKey) && (e.currentTarget.style.backgroundColor = 'transparent')}
                            >
                                <Icon className="w-4 h-4" />
                                <span>{item}</span>
                            </div>
                        );
                    })}
                </div>

                {/* Database Section */}
                <div className="mt-4 pt-4" style={{ borderTop: `1px solid ${darkMode ? '#374151' : '#e5e7eb'}` }}>
                    <div className="flex items-center gap-2 px-2 py-1.5 text-xs font-semibold uppercase tracking-wider" style={{ color: darkMode ? '#9ca3af' : '#6b7280' }}>
                        <Database className="w-3.5 h-3.5" />
                        <span>Database</span>
                    </div>
                    <div className="space-y-0.5 mt-1">
                        {/* Medicines - Clickable */}
                        <div
                            onClick={() => handleNavClick('medicines')}
                            className="flex items-center gap-2 px-2 py-1.5 rounded-md text-sm font-medium cursor-pointer pl-6 transition-colors"
                            style={getNavItemStyle('medicines')}
                        >
                            <Pill className="w-4 h-4" />
                            <span>Medicines</span>
                        </div>

                        {/* Other database items */}
                        {/* {[{ icon: Users, label: 'Patients' }, { icon: Building2, label: 'HCP Registry' }].map(({ icon: Icon, label }) => (
                            <div key={label} className="flex items-center gap-2 px-2 py-1.5 rounded-md text-sm font-medium cursor-pointer pl-6"
                                style={{ color: darkMode ? '#d1d5db' : '#4b5563' }}
                                onMouseEnter={(e) => e.currentTarget.style.backgroundColor = darkMode ? '#374151' : '#f3f4f6'}
                                onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}>
                                <Icon className="w-4 h-4" />
                                <span>{label}</span>
                            </div>
                        ))} */}
                    </div>
                </div>
            </nav>

            {/* Bottom Section */}
            <div className="px-2 pb-3 space-y-0.5 pt-3" style={{ borderTop: `1px solid ${darkMode ? '#374151' : '#e5e7eb'}` }}>
                {[{ icon: HelpCircle, label: 'Help & Support' }, { icon: Settings, label: 'Settings' }].map(({ icon: Icon, label }) => (
                    <div key={label} className="flex items-center gap-2 px-2 py-1.5 rounded-md text-sm font-medium cursor-pointer"
                        style={{ color: darkMode ? '#d1d5db' : '#4b5563' }}
                        onMouseEnter={(e) => e.currentTarget.style.backgroundColor = darkMode ? '#374151' : '#f3f4f6'}
                        onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}>
                        <Icon className="w-4 h-4" />
                        <span>{label}</span>
                    </div>
                ))}
            </div>

            {/* User Profile */}
            <div className="px-4 py-3" style={{ borderTop: `1px solid ${darkMode ? '#374151' : '#e5e7eb'}` }}>
                <div className="flex items-center gap-2">
                    <div className="w-8 h-8 rounded-full flex items-center justify-center" style={{ backgroundColor: '#073d44' }}>
                        <User className="w-4 h-4 text-white" />
                    </div>
                    <div className="flex-1 min-w-0">
                        <div className="text-sm font-medium" style={{ color: darkMode ? '#f9fafb' : '#111827' }}>EMP001</div>
                    </div>
                    <button
                        onClick={() => navigate('/')}
                        className="p-1.5 rounded-md transition-colors"
                        style={{ color: darkMode ? '#9ca3af' : '#6b7280' }}
                        onMouseEnter={(e) => e.currentTarget.style.backgroundColor = darkMode ? '#374151' : '#f3f4f6'}
                        onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
                        title="Logout"
                    >
                        <LogOut className="w-4 h-4" />
                    </button>
                </div>
            </div>
        </aside>
    );
};

export default Sidebar;
