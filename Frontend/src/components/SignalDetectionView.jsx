/**
 * Signal Detection View Component
 * Displays FAERS signals and potential safety signals analysis
 */
import React from 'react';
import { Activity, AlertTriangle, TrendingUp, Shield, Database } from 'lucide-react';
import useThemeStore from '../store/themeStore';

const SignalDetectionView = ({ faersSignals = [], faersStats = null }) => {
    const { darkMode } = useThemeStore();

    // Theme colors
    const theme = {
        bg: darkMode ? '#1f2937' : '#ffffff',
        bgSecondary: darkMode ? '#111827' : '#f9fafb',
        text: darkMode ? '#f9fafb' : '#111827',
        textSecondary: darkMode ? '#9ca3af' : '#6b7280',
        border: darkMode ? '#374151' : '#e5e7eb',
    };

    // Get signal strength badge style
    const getSignalBadgeStyle = (ic) => {
        if (ic > 3.0) return { bg: darkMode ? '#7f1d1d' : '#fee2e2', text: darkMode ? '#fca5a5' : '#dc2626' };
        if (ic > 1.5) return { bg: darkMode ? '#78350f' : '#fef3c7', text: darkMode ? '#fcd34d' : '#d97706' };
        return { bg: darkMode ? '#1e3a5f' : '#dbeafe', text: darkMode ? '#93c5fd' : '#2563eb' };
    };

    // Stat card component
    const StatCard = ({ label, value, icon: Icon, color }) => (
        <div
            className="rounded-lg p-5"
            style={{
                backgroundColor: theme.bg,
                border: `1px solid ${theme.border}`
            }}
        >
            <div className="flex items-center justify-between mb-3">
                <span className="text-sm font-medium" style={{ color: theme.textSecondary }}>
                    {label}
                </span>
                <Icon className="w-5 h-5" style={{ color }} />
            </div>
            <div className="text-3xl font-bold" style={{ color }}>
                {value}
            </div>
        </div>
    );

    return (
        <div className="p-6" style={{ backgroundColor: theme.bgSecondary }}>
            {/* Header */}
            <div className="mb-6">
                <h2 className="text-2xl font-bold mb-1" style={{ color: theme.text }}>
                    Signal Detection
                </h2>
                <p className="text-sm" style={{ color: theme.textSecondary }}>
                    FAERS-based BCPNN analysis for potential safety signals
                </p>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-4 gap-4 mb-6">
                <StatCard
                    label="Total Reports"
                    value={faersStats?.total_reports || 0}
                    icon={Database}
                    color="#073d44"
                />
                <StatCard
                    label="Signals Detected"
                    value={faersStats?.signals_detected || faersSignals.length}
                    icon={AlertTriangle}
                    color="#ef4444"
                />
                <StatCard
                    label="Unique Drugs"
                    value={faersStats?.unique_drugs || 0}
                    icon={Shield}
                    color="#3b82f6"
                />
                <StatCard
                    label="Unique Events"
                    value={faersStats?.unique_events || 0}
                    icon={TrendingUp}
                    color="#10b981"
                />
            </div>

            {/* Signals Table */}
            <div className="rounded-lg overflow-hidden" style={{ backgroundColor: theme.bg, border: `1px solid ${theme.border}` }}>
                <div className="px-5 py-4 flex items-center gap-2" style={{ borderBottom: `1px solid ${theme.border}` }}>
                    <Activity className="w-5 h-5" style={{ color: '#073d44' }} />
                    <h3 className="text-lg font-semibold" style={{ color: theme.text }}>
                        Potential Safety Signals
                    </h3>
                    <span className="ml-2 px-2 py-0.5 text-xs font-semibold rounded-full" style={{
                        backgroundColor: '#fee2e2',
                        color: '#dc2626'
                    }}>
                        {faersSignals.length} signals
                    </span>
                </div>

                {faersSignals.length > 0 ? (
                    <table className="w-full">
                        <thead>
                            <tr style={{ backgroundColor: theme.bgSecondary }}>
                                <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wider" style={{ color: theme.textSecondary }}>
                                    Suspect Product
                                </th>
                                <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wider" style={{ color: theme.textSecondary }}>
                                    Adverse Event
                                </th>
                                <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wider" style={{ color: theme.textSecondary }}>
                                    Observed / Expected
                                </th>
                                <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wider" style={{ color: theme.textSecondary }}>
                                    IC Score
                                </th>
                                <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wider" style={{ color: theme.textSecondary }}>
                                    Signal Strength
                                </th>
                            </tr>
                        </thead>
                        <tbody>
                            {faersSignals.map((signal, index) => {
                                const badgeStyle = getSignalBadgeStyle(signal?.ic || 0);
                                return (
                                    <tr
                                        key={index}
                                        style={{
                                            borderBottom: `1px solid ${theme.border}`,
                                            transition: 'background-color 0.15s ease'
                                        }}
                                        onMouseEnter={(e) => e.currentTarget.style.backgroundColor = darkMode ? '#374151' : '#f9fafb'}
                                        onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
                                    >
                                        <td className="px-5 py-4">
                                            <span className="font-medium" style={{ color: theme.text }}>
                                                {signal?.drug || 'Unknown'}
                                            </span>
                                        </td>
                                        <td className="px-5 py-4">
                                            <span style={{ color: theme.textSecondary }}>
                                                {signal?.event || 'Unknown'}
                                            </span>
                                        </td>
                                        <td className="px-5 py-4">
                                            <span className="font-mono text-sm" style={{ color: theme.text }}>
                                                {signal?.count || 0} / {signal?.expected_count || 0}
                                            </span>
                                        </td>
                                        <td className="px-5 py-4">
                                            <span className="font-mono font-semibold" style={{
                                                color: signal?.ic > 2 ? '#ef4444' : signal?.ic > 1 ? '#f59e0b' : theme.text
                                            }}>
                                                {typeof signal?.ic === 'number' ? signal.ic.toFixed(2) : 'N/A'}
                                            </span>
                                        </td>
                                        <td className="px-5 py-4">
                                            <span
                                                className="px-2.5 py-1 rounded-full text-xs font-semibold"
                                                style={{
                                                    backgroundColor: badgeStyle.bg,
                                                    color: badgeStyle.text
                                                }}
                                            >
                                                {signal?.signal_strength || ((signal?.ic || 0) > 3.0 ? 'Very Strong' : (signal?.ic || 0) > 1.5 ? 'Strong' : 'Moderate')}
                                            </span>
                                        </td>
                                    </tr>
                                );
                            })}
                        </tbody>
                    </table>
                ) : (
                    <div className="flex flex-col items-center justify-center py-16">
                        <Activity className="w-12 h-12 mb-3" style={{ color: theme.textSecondary }} />
                        <p className="text-sm" style={{ color: theme.textSecondary }}>No signals detected</p>
                    </div>
                )}
            </div>

            {/* Info Card */}
            <div className="mt-6 rounded-lg p-4" style={{
                backgroundColor: darkMode ? '#1e3a5f' : '#eff6ff',
                border: `1px solid ${darkMode ? '#3b82f6' : '#bfdbfe'}`
            }}>
                <div className="flex items-start gap-3">
                    <Shield className="w-5 h-5 mt-0.5" style={{ color: '#3b82f6' }} />
                    <div>
                        <h4 className="text-sm font-semibold mb-1" style={{ color: darkMode ? '#93c5fd' : '#1e40af' }}>
                            About IC Scores (Information Component)
                        </h4>
                        <p className="text-xs" style={{ color: darkMode ? '#bfdbfe' : '#3b82f6' }}>
                            IC scores measure disproportionate reporting. IC &gt; 0 indicates more reports than expected.
                            IC &gt; 2 suggests a strong signal requiring further investigation. IC &gt; 3 indicates very strong association.
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default SignalDetectionView;
