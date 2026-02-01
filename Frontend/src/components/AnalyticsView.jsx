/**
 * Analytics View Component
 * Displays charts and graphs for case analytics
 */
import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, Legend, LineChart, Line, Area, AreaChart } from 'recharts';
import { BarChart3, PieChart as PieChartIcon, TrendingUp, Activity, AlertTriangle, Clock, CheckSquare } from 'lucide-react';
import useThemeStore from '../store/themeStore';

const AnalyticsView = ({ caseReports = [] }) => {
    const { darkMode } = useThemeStore();

    // Theme colors
    const theme = {
        bg: darkMode ? '#1f2937' : '#ffffff',
        bgSecondary: darkMode ? '#111827' : '#f9fafb',
        text: darkMode ? '#f9fafb' : '#111827',
        textSecondary: darkMode ? '#9ca3af' : '#6b7280',
        border: darkMode ? '#374151' : '#e5e7eb',
        gridColor: darkMode ? '#374151' : '#e5e7eb',
    };

    // Color schemes for different chart types
    const SEVERITY_COLORS = {
        'Severe': '#ef4444',
        'Moderate': '#f59e0b',
        'Mild': '#6b7280',
        'Unknown': '#9ca3af'
    };

    const STATUS_COLORS = {
        'Pending': '#6366f1',
        'In Progress': '#3b82f6',
        'Escalated': '#ef4444',
        'Complete': '#10b981',
        'Unknown': '#9ca3af'
    };

    const DRUG_COLORS = ['#073d44', '#0a5c66', '#10b981', '#3b82f6', '#8b5cf6'];

    // Process data for Severity Chart
    const severityData = React.useMemo(() => {
        const counts = {};
        caseReports.forEach(c => {
            const severity = c.severity || 'Unknown';
            counts[severity] = (counts[severity] || 0) + 1;
        });
        return Object.entries(counts).map(([name, value]) => ({
            name,
            cases: value,
            fill: SEVERITY_COLORS[name] || '#9ca3af'
        }));
    }, [caseReports]);

    // Process data for Status Chart (Pie)
    const statusData = React.useMemo(() => {
        const counts = {};
        caseReports.forEach(c => {
            const status = c.status || 'Unknown';
            counts[status] = (counts[status] || 0) + 1;
        });
        return Object.entries(counts).map(([name, value]) => ({
            name,
            value,
            fill: STATUS_COLORS[name] || '#9ca3af'
        }));
    }, [caseReports]);

    // Process data for Drug Chart (Top 5 drugs)
    const drugData = React.useMemo(() => {
        const counts = {};
        caseReports.forEach(c => {
            const drug = c.drug || 'Unknown';
            counts[drug] = (counts[drug] || 0) + 1;
        });
        return Object.entries(counts)
            .sort((a, b) => b[1] - a[1])
            .slice(0, 5)
            .map(([name, value], index) => ({
                name: name.length > 15 ? name.slice(0, 12) + '...' : name,
                cases: value,
                fill: DRUG_COLORS[index % DRUG_COLORS.length]
            }));
    }, [caseReports]);

    // Process confidence score distribution
    const confidenceData = React.useMemo(() => {
        const ranges = {
            '0-20%': 0,
            '21-40%': 0,
            '41-60%': 0,
            '61-80%': 0,
            '81-100%': 0
        };

        caseReports.forEach(c => {
            const conf = c.confidence || 0;
            if (conf <= 20) ranges['0-20%']++;
            else if (conf <= 40) ranges['21-40%']++;
            else if (conf <= 60) ranges['41-60%']++;
            else if (conf <= 80) ranges['61-80%']++;
            else ranges['81-100%']++;
        });

        return Object.entries(ranges).map(([name, value]) => ({
            name,
            cases: value
        }));
    }, [caseReports]);

    // Custom tooltip
    const CustomTooltip = ({ active, payload, label }) => {
        if (active && payload && payload.length) {
            return (
                <div style={{
                    backgroundColor: darkMode ? '#1f2937' : '#ffffff',
                    border: `1px solid ${theme.border}`,
                    borderRadius: '8px',
                    padding: '12px',
                    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                }}>
                    <p style={{
                        color: theme.text,
                        fontWeight: '600',
                        marginBottom: '4px',
                        fontSize: '14px'
                    }}>
                        {label}
                    </p>
                    <p style={{
                        color: payload[0].fill || '#10b981',
                        fontWeight: '600',
                        fontSize: '16px'
                    }}>
                        {payload[0].value} {payload[0].dataKey === 'value' ? 'cases' : payload[0].dataKey}
                    </p>
                </div>
            );
        }
        return null;
    };

    // Chart card wrapper
    const ChartCard = ({ title, icon: Icon, children, className = '' }) => (
        <div
            className={`rounded-lg p-5 ${className}`}
            style={{
                backgroundColor: theme.bg,
                border: `1px solid ${theme.border}`,
                transition: 'all 0.3s ease'
            }}
        >
            <div className="flex items-center gap-2 mb-4">
                <Icon className="w-5 h-5" style={{ color: '#073d44' }} />
                <h3 className="text-base font-semibold" style={{ color: theme.text }}>
                    {title}
                </h3>
            </div>
            {children}
        </div>
    );

    // Stat card component
    const StatCard = ({ label, value, color, icon: Icon }) => (
        <div
            className="rounded-lg p-4"
            style={{
                backgroundColor: theme.bg,
                border: `1px solid ${theme.border}`
            }}
        >
            <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium" style={{ color: theme.textSecondary }}>
                    {label}
                </span>
                <Icon className="w-4 h-4" style={{ color }} />
            </div>
            <div className="text-2xl font-bold" style={{ color }}>
                {value}
            </div>
        </div>
    );

    return (
        <div className="p-6" style={{ backgroundColor: theme.bgSecondary }}>
            {/* Header */}
            <div className="mb-6">
                <h2 className="text-2xl font-bold mb-1" style={{ color: theme.text }}>
                    Analytics Overview
                </h2>
                <p className="text-sm" style={{ color: theme.textSecondary }}>
                    Visualizing {caseReports.length} adverse event cases
                </p>
            </div>

            {/* Summary Stats */}
            <div className="grid grid-cols-4 gap-4 mb-6">
                <StatCard
                    label="Total Cases"
                    value={caseReports.length}
                    color="#073d44"
                    icon={Activity}
                />
                <StatCard
                    label="Pending Review"
                    value={caseReports.filter(c => c.status === 'Pending').length}
                    color="#6366f1"
                    icon={Clock}
                />
                <StatCard
                    label="Completed"
                    value={caseReports.filter(c => c.status === 'Complete').length}
                    color="#10b981"
                    icon={CheckSquare}
                />
                <StatCard
                    label="Escalated"
                    value={caseReports.filter(c => c.status === 'Escalated').length}
                    color="#ef4444"
                    icon={AlertTriangle}
                />
            </div>

            {/* Charts Grid */}
            <div className="grid grid-cols-2 gap-6">
                {/* Cases by Severity */}
                <ChartCard title="Cases by Severity" icon={AlertTriangle}>
                    {severityData.length > 0 ? (
                        <ResponsiveContainer width="100%" height={280}>
                            <BarChart data={severityData}>
                                <CartesianGrid
                                    strokeDasharray="3 3"
                                    stroke={theme.gridColor}
                                    vertical={false}
                                />
                                <XAxis
                                    dataKey="name"
                                    tick={{ fill: theme.textSecondary, fontSize: 12 }}
                                    axisLine={{ stroke: theme.border }}
                                />
                                <YAxis
                                    tick={{ fill: theme.textSecondary, fontSize: 12 }}
                                    axisLine={{ stroke: theme.border }}
                                />
                                <Tooltip content={<CustomTooltip />} cursor={{ fill: darkMode ? '#374151' : '#f3f4f6' }} />
                                <Bar
                                    dataKey="cases"
                                    radius={[8, 8, 0, 0]}
                                />
                            </BarChart>
                        </ResponsiveContainer>
                    ) : (
                        <div className="h-64 flex items-center justify-center" style={{ color: theme.textSecondary }}>
                            No data available
                        </div>
                    )}
                </ChartCard>

                {/* Cases by Status (Pie Chart) */}
                <ChartCard title="Cases by Status" icon={PieChartIcon}>
                    {statusData.length > 0 ? (
                        <ResponsiveContainer width="100%" height={280}>
                            <PieChart>
                                <Pie
                                    data={statusData}
                                    cx="50%"
                                    cy="50%"
                                    labelLine={false}
                                    label={({ name, percent }) => `${name} (${(percent * 100).toFixed(0)}%)`}
                                    outerRadius={90}
                                    dataKey="value"
                                >
                                    {statusData.map((entry, index) => (
                                        <Cell key={`cell-${index}`} fill={entry.fill} />
                                    ))}
                                </Pie>
                                <Tooltip content={<CustomTooltip />} />
                                <Legend
                                    wrapperStyle={{ fontSize: '12px', color: theme.textSecondary }}
                                    iconType="circle"
                                />
                            </PieChart>
                        </ResponsiveContainer>
                    ) : (
                        <div className="h-64 flex items-center justify-center" style={{ color: theme.textSecondary }}>
                            No data available
                        </div>
                    )}
                </ChartCard>

                {/* Top 5 Drugs */}
                <ChartCard title="Top 5 Drugs" icon={BarChart3}>
                    {drugData.length > 0 ? (
                        <ResponsiveContainer width="100%" height={280}>
                            <BarChart data={drugData} layout="vertical">
                                <CartesianGrid
                                    strokeDasharray="3 3"
                                    stroke={theme.gridColor}
                                    horizontal={false}
                                />
                                <XAxis
                                    type="number"
                                    tick={{ fill: theme.textSecondary, fontSize: 12 }}
                                    axisLine={{ stroke: theme.border }}
                                />
                                <YAxis
                                    dataKey="name"
                                    type="category"
                                    tick={{ fill: theme.textSecondary, fontSize: 12 }}
                                    axisLine={{ stroke: theme.border }}
                                    width={100}
                                />
                                <Tooltip content={<CustomTooltip />} cursor={{ fill: darkMode ? '#374151' : '#f3f4f6' }} />
                                <Bar
                                    dataKey="cases"
                                    radius={[0, 8, 8, 0]}
                                />
                            </BarChart>
                        </ResponsiveContainer>
                    ) : (
                        <div className="h-64 flex items-center justify-center" style={{ color: theme.textSecondary }}>
                            No data available
                        </div>
                    )}
                </ChartCard>

                {/* Confidence Score Distribution */}
                <ChartCard title="Confidence Score Distribution" icon={TrendingUp}>
                    {confidenceData.length > 0 ? (
                        <ResponsiveContainer width="100%" height={280}>
                            <AreaChart data={confidenceData}>
                                <defs>
                                    <linearGradient id="colorConfidence" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#073d44" stopOpacity={0.8} />
                                        <stop offset="95%" stopColor="#073d44" stopOpacity={0.1} />
                                    </linearGradient>
                                </defs>
                                <CartesianGrid
                                    strokeDasharray="3 3"
                                    stroke={theme.gridColor}
                                    vertical={false}
                                />
                                <XAxis
                                    dataKey="name"
                                    tick={{ fill: theme.textSecondary, fontSize: 12 }}
                                    axisLine={{ stroke: theme.border }}
                                />
                                <YAxis
                                    tick={{ fill: theme.textSecondary, fontSize: 12 }}
                                    axisLine={{ stroke: theme.border }}
                                />
                                <Tooltip content={<CustomTooltip />} />
                                <Area
                                    type="monotone"
                                    dataKey="cases"
                                    stroke="#073d44"
                                    fillOpacity={1}
                                    fill="url(#colorConfidence)"
                                    strokeWidth={2}
                                />
                            </AreaChart>
                        </ResponsiveContainer>
                    ) : (
                        <div className="h-64 flex items-center justify-center" style={{ color: theme.textSecondary }}>
                            No data available
                        </div>
                    )}
                </ChartCard>
            </div>
        </div>
    );
};

export default AnalyticsView;