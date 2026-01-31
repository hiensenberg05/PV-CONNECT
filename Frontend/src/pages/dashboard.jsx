import React, { useState } from 'react';
import { Search, ChevronDown, Plus, MoreHorizontal, Bell, LayoutDashboard, Mail, CheckSquare, FileText, BarChart3, Zap, GitBranch, Star, Database, Building2, Users, Settings, HelpCircle, User, Filter, Download, Eye, EyeOff, Grid3x3, Columns, List, MapPin, TrendingUp, TrendingDown, ChevronRight, AlertTriangle, Activity, Shield, Clock, Calendar, Moon, Sun } from 'lucide-react';
import AddCaseReportModal from '../components/AddCaseReportModal';
import CaseDetailsModal from '../components/CaseDetailsModal';
import MedicinesTable from '../components/MedicinesTable';
import AnalyticsView from '../components/AnalyticsView';
import Sidebar from '../components/Sidebar';
import useThemeStore from '../store/themeStore';
import useAnalytics from '../hooks/useAnalytics';

const Dashboard = () => {
    const [viewMode, setViewMode] = useState('table');
    const [activeView, setActiveView] = useState('dashboard');
    const { darkMode, toggleDarkMode } = useThemeStore();
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [isDetailsModalOpen, setIsDetailsModalOpen] = useState(false);
    const [selectedCase, setSelectedCase] = useState(null);
    const [searchQuery, setSearchQuery] = useState('');
    const [caseReports, setCaseReports] = useState([]);


    // Fetch analytics data from backend
    const { statistics, cases, loading, error, refetch } = useAnalytics();

    // Sync cases from backend to local state
    React.useEffect(() => {
        if (cases && cases.length > 0) {
            // Transform backend case format to dashboard format
            const transformedCases = cases.map((c, index) => ({
                id: c.case_id || `AE-${index + 1}`,
                patient: c.data?.patient_details?.name || c.patient_name || 'Unknown',
                location: c.data?.patient_details?.country || 'Unknown',
                drug: c.data?.medicine_details?.[0]?.name || 'Unknown',
                event: c.data?.description || c.data?.reaction_details?.event_term || 'Unknown',
                severity: c.data?.severity?.[0] || 'Unknown',
                status: c.status || 'Pending',
                completeness: Math.round((c.confidence_score || 0) * 100),
                confidence: Math.round((c.confidence_score || 0) * 100),
                _raw: c // Store original raw data for modal
            }));
            setCaseReports(transformedCases);
        }
    }, [cases]);

    const handleAddCase = (newCase) => {
        setCaseReports(prev => [newCase, ...prev]);
        // Optionally refetch to sync with backend
        refetch();
    };

    // Filter cases based on search query
    const filteredCases = caseReports.filter(report => {
        if (!searchQuery.trim()) return true;
        const query = searchQuery.toLowerCase();
        return (
            report.id.toLowerCase().includes(query) ||
            report.patient.toLowerCase().includes(query) ||
            report.drug.toLowerCase().includes(query) ||
            report.event.toLowerCase().includes(query) ||
            report.location.toLowerCase().includes(query) ||
            report.severity.toLowerCase().includes(query) ||
            report.status.toLowerCase().includes(query)
        );
    });

    const getSeverityColor = (severity) => {
        if (darkMode) {
            switch (severity) {
                case 'Severe': return { bg: '#374151', text: '#f87171', border: '#4b5563' };
                case 'Moderate': return { bg: '#374151', text: '#fbbf24', border: '#4b5563' };
                case 'Mild': return { bg: '#374151', text: '#9ca3af', border: '#4b5563' };
                default: return { bg: '#374151', text: '#d1d5db', border: '#4b5563' };
            }
        }
        switch (severity) {
            case 'Severe': return { bg: '#f9fafb', text: '#dc2626', border: '#e5e7eb' };
            case 'Moderate': return { bg: '#f9fafb', text: '#d97706', border: '#e5e7eb' };
            case 'Mild': return { bg: '#f9fafb', text: '#6b7280', border: '#e5e7eb' };
            default: return { bg: '#f3f4f6', text: '#374151', border: '#e5e7eb' };
        }
    };

    const getStatusColor = (status) => {
        if (darkMode) {
            switch (status) {
                case 'Pending': return { bg: '#374151', text: '#a5b4fc', border: '#4b5563' };
                case 'In Progress': return { bg: '#374151', text: '#60a5fa', border: '#4b5563' };
                case 'Escalated': return { bg: '#374151', text: '#f87171', border: '#4b5563' };
                case 'Complete': return { bg: '#374151', text: '#4ade80', border: '#4b5563' };
                default: return { bg: '#374151', text: '#d1d5db', border: '#4b5563' };
            }
        }
        switch (status) {
            case 'Pending': return { bg: '#f9fafb', text: '#6366f1', border: '#e5e7eb' };
            case 'In Progress': return { bg: '#f9fafb', text: '#3b82f6', border: '#e5e7eb' };
            case 'Escalated': return { bg: '#f9fafb', text: '#dc2626', border: '#e5e7eb' };
            case 'Complete': return { bg: '#f9fafb', text: '#16a34a', border: '#e5e7eb' };
            default: return { bg: '#f3f4f6', text: '#374151', border: '#e5e7eb' };
        }
    };

    return (
        <div className="flex h-screen overflow-hidden" style={{
            fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, sans-serif',
            backgroundColor: darkMode ? '#111827' : '#f9fafb',
            transition: 'background-color 0.3s ease'
        }}>
            {/* Sidebar */}
            <Sidebar activeView={activeView} onViewChange={setActiveView} />

            {/* Main Content */}
            <div className="flex-1 flex flex-col overflow-hidden">
                {/* Top Bar */}
                <header className="px-6 py-3 flex items-center justify-between" style={{
                    backgroundColor: darkMode ? '#1f2937' : '#ffffff',
                    borderBottom: `1px solid ${darkMode ? '#374151' : '#e5e7eb'}`,
                    transition: 'all 0.3s ease'
                }}>
                    <div className="flex items-center gap-3">
                        {activeView === 'medicines' ? (
                            <>
                                <Database className="w-5 h-5" style={{ color: darkMode ? '#9ca3af' : '#9ca3af' }} />
                                <h1 className="text-lg font-semibold" style={{ color: darkMode ? '#f9fafb' : '#111827' }}>Medicines Database</h1>
                                <span className="text-sm" style={{ color: darkMode ? '#9ca3af' : '#6b7280' }}>• Drug Reference Library</span>
                            </>
                        ) : activeView === 'analytics' ? (
                            <>
                                <BarChart3 className="w-5 h-5" style={{ color: darkMode ? '#9ca3af' : '#9ca3af' }} />
                                <h1 className="text-lg font-semibold" style={{ color: darkMode ? '#f9fafb' : '#111827' }}>Analytics & Insights</h1>
                                <span className="text-sm" style={{ color: darkMode ? '#9ca3af' : '#6b7280' }}>• Data Visualization</span>
                            </>
                        ) : (
                            <>
                                <AlertTriangle className="w-5 h-5" style={{ color: darkMode ? '#9ca3af' : '#9ca3af' }} />
                                <h1 className="text-lg font-semibold" style={{ color: darkMode ? '#f9fafb' : '#111827' }}>Adverse Event Reports</h1>
                                <span className="text-sm" style={{ color: darkMode ? '#9ca3af' : '#6b7280' }}>• {caseReports.length} active cases</span>
                            </>
                        )}
                    </div>
                    <div className="flex items-center gap-3">
                        {/* Night Mode Toggle */}
                        <button
                            onClick={toggleDarkMode}
                            className="p-2 rounded-md transition-colors"
                            style={{
                                backgroundColor: darkMode ? '#374151' : '#f3f4f6',
                                color: darkMode ? '#fbbf24' : '#6b7280'
                            }}
                            onMouseEnter={(e) => e.currentTarget.style.backgroundColor = darkMode ? '#4b5563' : '#e5e7eb'}
                            onMouseLeave={(e) => e.currentTarget.style.backgroundColor = darkMode ? '#374151' : '#f3f4f6'}
                        >
                            {darkMode ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
                        </button>

                        {/* <button className="px-3 py-1.5 text-sm font-medium rounded-md flex items-center gap-1.5" style={{
                            color: darkMode ? '#d1d5db' : '#374151',
                            backgroundColor: darkMode ? '#1f2937' : '#ffffff',
                            border: `1px solid ${darkMode ? '#4b5563' : '#d1d5db'}`
                        }}>
                            <Calendar className="w-4 h-4" />
                            Export Reports
                        </button> */}
                        {activeView === 'dashboard' && (
                            <button
                                onClick={() => setIsModalOpen(true)}
                                className="px-3 py-1.5 text-sm font-medium text-white rounded-md flex items-center gap-1.5 transition-colors" style={{ backgroundColor: '#073d44' }}
                                onMouseEnter={(e) => e.target.style.backgroundColor = '#0a5c66'}
                                onMouseLeave={(e) => e.target.style.backgroundColor = '#073d44'}>
                                <Plus className="w-4 h-4" />
                                New Case Report
                            </button>
                        )}
                    </div>
                </header>

                {/* Main Content Area */}
                <main className="flex-1 overflow-y-auto">
                    {activeView === 'dashboard' && (
                        <>
                            {/* Metrics */}
                            <div className="px-6 py-6 grid grid-cols-6 gap-4">
                                {[
                                    { icon: FileText, label: 'Total Cases', value: loading ? '...' : String(statistics?.total_cases_scored || caseReports.length || 0), trend: null },
                                    { icon: Clock, label: 'Pending Review', value: loading ? '...' : String(caseReports.filter(c => c.status === 'Pending').length), trend: null },
                                    { icon: CheckSquare, label: 'Completed', value: loading ? '...' : String(caseReports.filter(c => c.status === 'Complete').length), trend: null },
                                    { icon: AlertTriangle, label: 'Escalated', value: loading ? '...' : String(caseReports.filter(c => c.status === 'Escalated').length), trend: null },
                                    { icon: Activity, label: 'Avg. Score', value: loading ? '...' : `${Math.round((statistics?.overall_average_score || 0) * 100)}%`, trend: null },
                                    { icon: TrendingUp, label: 'In Progress', value: loading ? '...' : String(caseReports.filter(c => c.status === 'In Progress').length), trend: null }
                                ].map(({ icon: Icon, label, value, trend, positive }) => (
                                    <div key={label} className="rounded-lg p-4" style={{
                                        backgroundColor: darkMode ? '#1f2937' : '#ffffff',
                                        border: `1px solid ${darkMode ? '#374151' : '#e5e7eb'}`
                                    }}>
                                        <div className="flex items-center gap-2 mb-2">
                                            <Icon className="w-4 h-4" style={{ color: darkMode ? '#9ca3af' : '#9ca3af' }} />
                                            <span className="text-sm" style={{ color: darkMode ? '#d1d5db' : '#6b7280' }}>{label}</span>
                                        </div>
                                        <div className="flex items-end justify-between">
                                            <div>
                                                <div className="text-2xl font-semibold" style={{ color: darkMode ? '#f9fafb' : '#111827' }}>{value}</div>
                                                {trend && (
                                                    <div className="text-xs" style={{ color: positive ? '#10b981' : '#ef4444' }}>{trend}</div>
                                                )}
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>

                            {/* Table Controls */}
                            <div className="px-6 pb-4">
                                <div className="rounded-lg" style={{
                                    backgroundColor: darkMode ? '#1f2937' : '#ffffff',
                                    border: `1px solid ${darkMode ? '#374151' : '#e5e7eb'}`
                                }}>
                                    <div className="px-4 py-3 flex items-center justify-between" style={{ borderBottom: `1px solid ${darkMode ? '#374151' : '#e5e7eb'}` }}>
                                        {/* Search Bar on Left */}
                                        <div className="flex items-center gap-2">
                                            <div className="relative">
                                                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4" style={{ color: darkMode ? '#6b7280' : '#9ca3af' }} />
                                                <input
                                                    type="text"
                                                    placeholder="Search cases..."
                                                    value={searchQuery}
                                                    onChange={(e) => setSearchQuery(e.target.value)}
                                                    className="pl-9 pr-4 py-1.5 text-sm rounded-md outline-none transition-all w-64"
                                                    style={{
                                                        backgroundColor: darkMode ? '#111827' : '#f9fafb',
                                                        border: `1px solid ${darkMode ? '#374151' : '#e5e7eb'}`,
                                                        color: darkMode ? '#f9fafb' : '#111827'
                                                    }}
                                                    onFocus={(e) => e.target.style.borderColor = '#073d44'}
                                                    onBlur={(e) => e.target.style.borderColor = darkMode ? '#374151' : '#e5e7eb'}
                                                />
                                            </div>
                                        </div>
                                        {/* Filters and Export on Right */}
                                        <div className="flex items-center gap-2">
                                            {[
                                                { icon: AlertTriangle, label: 'Severity' },
                                                { icon: FileText, label: 'Status' },
                                            ].map(({ icon: Icon, label }) => (
                                                <button key={label} className="flex items-center gap-1.5 px-2.5 py-1.5 text-sm font-medium rounded-md" style={{
                                                    color: darkMode ? '#d1d5db' : '#374151',
                                                    backgroundColor: darkMode ? '#1f2937' : '#ffffff',
                                                    border: `1px solid ${darkMode ? '#4b5563' : '#d1d5db'}`
                                                }}>
                                                    <Icon className="w-3.5 h-3.5" />
                                                    {label}
                                                    <ChevronDown className="w-3.5 h-3.5" />
                                                </button>
                                            ))}
                                            <button className="flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium rounded-md" style={{
                                                color: darkMode ? '#d1d5db' : '#374151',
                                                backgroundColor: darkMode ? '#111827' : '#ffffff',
                                                border: `1px solid ${darkMode ? '#4b5563' : '#d1d5db'}`
                                            }}>
                                                <Download className="w-4 h-4" />
                                                Export
                                            </button>
                                        </div>
                                    </div>

                                    {/* Filter Bar */}
                                    {/* <div className="px-4 py-3 flex items-center gap-2" style={{
                                borderBottom: `1px solid ${darkMode ? '#374151' : '#e5e7eb'}`,
                                backgroundColor: darkMode ? '#111827' : '#f9fafb'
                            }}>
                                {[
                                    { icon: AlertTriangle, label: 'Severity' },
                                    { icon: FileText, label: 'Status' },
                                    { icon: User, label: 'Reporter' }
                                ].map(({ icon: Icon, label }) => (
                                    <button key={label} className="flex items-center gap-1.5 px-2.5 py-1 text-sm font-medium rounded-md" style={{
                                        color: darkMode ? '#d1d5db' : '#374151',
                                        backgroundColor: darkMode ? '#1f2937' : '#ffffff',
                                        border: `1px solid ${darkMode ? '#4b5563' : '#d1d5db'}`
                                    }}>
                                        <Icon className="w-3.5 h-3.5" />
                                        {label}
                                        <ChevronDown className="w-3.5 h-3.5" />
                                    </button>
                                ))}
                                <button className="flex items-center gap-1.5 px-2.5 py-1 text-sm font-medium rounded-md" style={{
                                    color: darkMode ? '#9ca3af' : '#6b7280'
                                }}>
                                    <Plus className="w-3.5 h-3.5" />
                                    Add filter
                                </button>
                            </div> */}

                                    {/* Table */}
                                    <div className="overflow-x-auto">
                                        <table className="w-full">
                                            <thead style={{
                                                backgroundColor: darkMode ? '#111827' : '#f9fafb',
                                                borderBottom: `1px solid ${darkMode ? '#374151' : '#e5e7eb'}`
                                            }}>
                                                <tr>
                                                    {['Case ID', 'Patient', 'Drug', 'Event', 'Severity', 'Status', 'Completeness', 'Confidence', 'Actions'].map((header) => (
                                                        <th key={header} className="px-4 py-2 text-left">
                                                            <span className="text-xs font-medium uppercase" style={{ color: darkMode ? '#9ca3af' : '#6b7280' }}>{header}</span>
                                                        </th>
                                                    ))}
                                                </tr>
                                            </thead>
                                            <tbody style={{
                                                backgroundColor: darkMode ? '#1f2937' : '#ffffff'
                                            }}>
                                                {filteredCases.map((report, index) => {
                                                    const severityColor = getSeverityColor(report.severity);
                                                    const statusColor = getStatusColor(report.status);
                                                    return (
                                                        <tr key={index} style={{
                                                            borderBottom: `1px solid ${darkMode ? '#374151' : '#e5e7eb'}`,
                                                            backgroundColor: darkMode ? '#1f2937' : '#ffffff',
                                                            transition: 'background-color 0.15s ease'
                                                        }}
                                                            onMouseEnter={(e) => e.currentTarget.style.backgroundColor = darkMode ? '#374151' : '#f9fafb'}
                                                            onMouseLeave={(e) => e.currentTarget.style.backgroundColor = darkMode ? '#1f2937' : '#ffffff'}>
                                                            <td className="px-4 py-3">
                                                                <span className="text-sm font-medium" style={{ color: '#3b82f6' }}>{report.id}</span>
                                                            </td>
                                                            <td className="px-4 py-3">
                                                                <div>
                                                                    <div className="text-sm font-medium" style={{ color: darkMode ? '#f9fafb' : '#111827' }}>{report.patient}</div>
                                                                    <div className="text-xs" style={{ color: darkMode ? '#9ca3af' : '#6b7280' }}>{report.location}</div>
                                                                </div>
                                                            </td>
                                                            <td className="px-4 py-3">
                                                                <span className="text-sm" style={{ color: darkMode ? '#d1d5db' : '#374151' }}>{report.drug}</span>
                                                            </td>
                                                            <td className="px-4 py-3">
                                                                <span className="text-sm" style={{ color: darkMode ? '#d1d5db' : '#374151' }}>{report.event}</span>
                                                            </td>
                                                            <td className="px-4 py-3">
                                                                <span
                                                                    className="inline-flex items-center px-2 py-1 text-xs font-medium rounded-md"
                                                                    style={{
                                                                        backgroundColor: severityColor.bg,
                                                                        color: severityColor.text
                                                                    }}
                                                                >
                                                                    {report.severity}
                                                                </span>
                                                            </td>
                                                            <td className="px-4 py-3">
                                                                <span
                                                                    className="inline-flex items-center px-2 py-1 text-xs font-medium rounded-md"
                                                                    style={{
                                                                        backgroundColor: statusColor.bg,
                                                                        color: statusColor.text
                                                                    }}
                                                                >
                                                                    {report.status}
                                                                </span>
                                                            </td>
                                                            <td className="px-4 py-3">
                                                                <div className="flex items-center gap-2">
                                                                    <div className="flex-1 rounded-full h-1.5" style={{ backgroundColor: darkMode ? '#374151' : '#e5e7eb' }}>
                                                                        <div
                                                                            className="h-1.5 rounded-full"
                                                                            style={{
                                                                                width: `${report.completeness}%`,
                                                                                backgroundColor: '#10b981'
                                                                            }}
                                                                        ></div>
                                                                    </div>
                                                                    <span className="text-xs w-8" style={{ color: darkMode ? '#d1d5db' : '#6b7280' }}>{report.completeness}%</span>
                                                                </div>
                                                            </td>
                                                            <td className="px-4 py-3">
                                                                <span className="text-sm font-medium" style={{ color: '#10b981' }}>{report.confidence}%</span>
                                                            </td>
                                                            <td className="px-4 py-3">
                                                                <div className="flex items-center gap-2">
                                                                    <button
                                                                        onClick={() => {
                                                                            setSelectedCase(report);
                                                                            setIsDetailsModalOpen(true);
                                                                        }}
                                                                        className="p-1 rounded transition-colors"
                                                                        style={{ color: darkMode ? '#9ca3af' : '#9ca3af' }}
                                                                        onMouseEnter={(e) => e.currentTarget.style.color = '#3b82f6'}
                                                                        onMouseLeave={(e) => e.currentTarget.style.color = darkMode ? '#9ca3af' : '#9ca3af'}
                                                                        title="View Details"
                                                                    >
                                                                        <Eye className="w-4 h-4" />
                                                                    </button>
                                                                    <button style={{ color: darkMode ? '#9ca3af' : '#9ca3af' }}>
                                                                        <MoreHorizontal className="w-4 h-4" />
                                                                    </button>
                                                                </div>
                                                            </td>
                                                        </tr>
                                                    );
                                                })}
                                            </tbody>
                                        </table>
                                    </div>
                                </div>
                            </div>
                        </>
                    )}

                    {/* Medicines Database Section */}
                    {activeView === 'medicines' && (
                        <div className="p-6">
                            <MedicinesTable />
                        </div>
                    )}

                    {/* Analytics Section */}
                    {activeView === 'analytics' && (
                        <AnalyticsView
                            caseReports={caseReports}
                            faersSignals={faersSignals}
                            faersStats={faersStats}
                        />
                    )}
                </main>
            </div>

            {/* Add Case Report Modal */}
            <AddCaseReportModal
                isOpen={isModalOpen}
                onClose={() => setIsModalOpen(false)}
                onAddCase={handleAddCase}
            />

            {/* Case Details Modal */}
            <CaseDetailsModal
                isOpen={isDetailsModalOpen}
                onClose={() => {
                    setIsDetailsModalOpen(false);
                    setSelectedCase(null);
                }}
                caseData={selectedCase}
                rawCaseData={selectedCase?._raw}
            />
        </div>
    );
};

export default Dashboard;