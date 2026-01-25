import React, { useState } from 'react';
import { Search, ChevronDown, Plus, MoreHorizontal, Bell, LayoutDashboard, Mail, CheckSquare, FileText, BarChart3, Zap, GitBranch, Star, Database, Building2, Users, Settings, HelpCircle, User, Filter, Download, Eye, EyeOff, Grid3x3, Columns, List, MapPin, TrendingUp, TrendingDown, ChevronRight, AlertTriangle, Activity, Shield, Clock, Calendar } from 'lucide-react';

const Dashboard = () => {
    const [viewMode, setViewMode] = useState('table');

    const caseReports = [
        { id: 'AE-2024-001', patient: 'Rahul Sharma', location: 'India', drug: 'Metformin 500mg', event: 'Nausea and vomiting', severity: 'Moderate', status: 'Complete', completeness: 95, confidence: 88 },
        { id: 'AE-2024-002', patient: 'Maria Garcia', location: 'Spain', drug: 'Lisinopril 10mg', event: 'Dry cough', severity: 'Mild', status: 'In Progress', completeness: 72, confidence: 75 },
        { id: 'AE-2024-003', patient: 'John Williams', location: 'USA', drug: 'Atorvastatin 20mg', event: 'Muscle pain and weakness', severity: 'Severe', status: 'Escalated', completeness: 88, confidence: 92 },
        { id: 'AE-2024-004', patient: 'Akiko Tanaka', location: 'Japan', drug: 'Omeprazole 40mg', event: 'Headache and dizziness', severity: 'Mild', status: 'Pending', completeness: 45, confidence: 55 },
        { id: 'AE-2024-005', patient: 'Hans Mueller', location: 'Germany', drug: 'Amlodipine 5mg', event: 'Ankle swelling', severity: 'Moderate', status: 'Complete', completeness: 100, confidence: 95 },
        { id: 'AE-2024-006', patient: 'Sophie Laurent', location: 'France', drug: 'Warfarin 5mg', event: 'Minor bruising', severity: 'Mild', status: 'In Progress', completeness: 68, confidence: 70 },
        { id: 'AE-2024-007', patient: 'Chen Wei', location: 'China', drug: 'Simvastatin 40mg', event: 'Muscle weakness', severity: 'Moderate', status: 'Complete', completeness: 92, confidence: 89 },
        { id: 'AE-2024-008', patient: 'Emma Thompson', location: 'UK', drug: 'Aspirin 100mg', event: 'Stomach discomfort', severity: 'Mild', status: 'Pending', completeness: 52, confidence: 60 },
        { id: 'AE-2024-009', patient: 'Carlos Rodriguez', location: 'Mexico', drug: 'Losartan 50mg', event: 'Dizziness', severity: 'Moderate', status: 'In Progress', completeness: 78, confidence: 82 },
        { id: 'AE-2024-010', patient: 'Yuki Nakamura', location: 'Japan', drug: 'Clopidogrel 75mg', event: 'Bleeding gums', severity: 'Mild', status: 'Complete', completeness: 98, confidence: 94 },
        { id: 'AE-2024-011', patient: 'Oliver Schmidt', location: 'Germany', drug: 'Ramipril 10mg', event: 'Persistent cough', severity: 'Mild', status: 'In Progress', completeness: 65, confidence: 68 },
        { id: 'AE-2024-012', patient: 'Isabella Romano', location: 'Italy', drug: 'Furosemide 40mg', event: 'Dehydration', severity: 'Moderate', status: 'Escalated', completeness: 85, confidence: 88 },
        { id: 'AE-2024-013', patient: 'Mohammed Al-Rashid', location: 'UAE', drug: 'Digoxin 0.25mg', event: 'Irregular heartbeat', severity: 'Severe', status: 'Escalated', completeness: 90, confidence: 93 },
        { id: 'AE-2024-014', patient: 'Anna Kowalski', location: 'Poland', drug: 'Levothyroxine 100mcg', event: 'Insomnia', severity: 'Mild', status: 'Pending', completeness: 48, confidence: 52 },
        { id: 'AE-2024-015', patient: 'Lucas Silva', location: 'Brazil', drug: 'Metoprolol 50mg', event: 'Fatigue', severity: 'Moderate', status: 'Complete', completeness: 96, confidence: 91 },
    ];

    const getSeverityColor = (severity) => {
        switch (severity) {
            case 'Severe': return { bg: '#fee2e2', text: '#991b1b', border: '#fecaca' };
            case 'Moderate': return { bg: '#fef3c7', text: '#92400e', border: '#fde68a' };
            case 'Mild': return { bg: '#dbeafe', text: '#1e40af', border: '#bfdbfe' };
            default: return { bg: '#f3f4f6', text: '#374151', border: '#e5e7eb' };
        }
    };

    const getStatusColor = (status) => {
        switch (status) {
            case 'Pending': return { bg: '#e0e7ff', text: '#3730a3', border: '#c7d2fe' };
            case 'In Progress': return { bg: '#dbeafe', text: '#1e40af', border: '#bfdbfe' };
            case 'Escalated': return { bg: '#fee2e2', text: '#991b1b', border: '#fecaca' };
            case 'Complete': return { bg: '#d1fae5', text: '#065f46', border: '#a7f3d0' };
            default: return { bg: '#f3f4f6', text: '#374151', border: '#e5e7eb' };
        }
    };

    const getPriorityColor = (priority) => {
        switch (priority) {
            case 'High': return { bg: '#fee2e2', text: '#991b1b', border: '#fecaca' };
            case 'Medium': return { bg: '#fed7aa', text: '#9a3412', border: '#fdba74' };
            case 'Low': return { bg: '#d1fae5', text: '#065f46', border: '#a7f3d0' };
            default: return { bg: '#f3f4f6', text: '#374151', border: '#e5e7eb' };
        }
    };

    return (
        <div className="flex h-screen overflow-hidden" style={{ fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, sans-serif', backgroundColor: '#f9fafb' }}>
            {/* Sidebar */}
            <aside className="w-56 bg-white flex flex-col" style={{ borderRight: '1px solid #e5e7eb' }}>
                {/* Logo */}
                <div className="px-4 py-4">
                    <div className="flex items-center gap-2">
                        <div className="w-7 h-7 rounded-md flex items-center justify-center" style={{ backgroundColor: '#073d44' }}>
                            <svg fill="#ffffff" width="16" height="16" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                                <path d="m21.743 12.331-9-10c-.379-.422-1.107-.422-1.486 0l-9 10a.998.998 0 0 0-.17 1.076c.16.361.518.593.913.593h2v7a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-7h2a.998.998 0 0 0 .743-1.669zM16 15h-3v3h-2v-3H8v-2h3v-3h2v3h3v2z" />
                            </svg>
                        </div>
                        <div>
                            <div className="text-sm font-semibold text-gray-900">NOVA</div>
                            <div className="text-xs text-gray-500">Pharmacovigilance</div>
                        </div>
                        <ChevronDown className="w-4 h-4 text-gray-400 ml-auto" />
                    </div>
                </div>

                {/* Search */}
                <div className="px-4 pb-3">
                    <div className="relative">
                        <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                        <input
                            type="text"
                            placeholder="Search cases..."
                            className="w-full pl-8 pr-8 py-1.5 text-sm bg-gray-50 border border-gray-200 rounded-md outline-none focus:border-gray-300"
                        />
                        <kbd className="absolute right-2 top-1/2 -translate-y-1/2 px-1.5 py-0.5 text-xs font-medium text-gray-500 bg-white border border-gray-200 rounded">⌘K</kbd>
                    </div>
                </div>

                {/* Main Navigation */}
                <nav className="flex-1 px-2 overflow-y-auto">
                    <div className="space-y-0.5">
                        <div className="flex items-center gap-2 px-2 py-1.5 rounded-md text-sm font-medium text-white cursor-pointer" style={{ backgroundColor: '#073d44' }}>
                            <LayoutDashboard className="w-4 h-4" />
                            <span>Dashboard</span>
                        </div>
                        <div className="flex items-center justify-between gap-2 px-2 py-1.5 rounded-md text-sm font-medium text-gray-600 hover:bg-gray-50 cursor-pointer">
                            <div className="flex items-center gap-2">
                                <Bell className="w-4 h-4" />
                                <span>Alerts</span>
                            </div>
                            <span className="px-1.5 py-0.5 text-xs font-semibold text-white rounded" style={{ backgroundColor: '#073d44' }}>8</span>
                        </div>
                        <div className="flex items-center gap-2 px-2 py-1.5 rounded-md text-sm font-medium text-gray-600 hover:bg-gray-50 cursor-pointer">
                            <FileText className="w-4 h-4" />
                            <span>Case Reports</span>
                        </div>
                        <div className="flex items-center gap-2 px-2 py-1.5 rounded-md text-sm font-medium text-gray-600 hover:bg-gray-50 cursor-pointer">
                            <Activity className="w-4 h-4" />
                            <span>Signal Detection</span>
                        </div>
                        <div className="flex items-center gap-2 px-2 py-1.5 rounded-md text-sm font-medium text-gray-600 hover:bg-gray-50 cursor-pointer">
                            <Shield className="w-4 h-4" />
                            <span>Safety Reports</span>
                        </div>
                        <div className="flex items-center gap-2 px-2 py-1.5 rounded-md text-sm font-medium text-gray-600 hover:bg-gray-50 cursor-pointer">
                            <BarChart3 className="w-4 h-4" />
                            <span>Analytics</span>
                        </div>
                        <div className="flex items-center justify-between gap-2 px-2 py-1.5 rounded-md text-sm font-medium text-gray-600 hover:bg-gray-50 cursor-pointer">
                            <div className="flex items-center gap-2">
                                <Zap className="w-4 h-4" />
                                <span>AI Insights</span>
                            </div>
                            <ChevronRight className="w-3 h-3" />
                        </div>
                        <div className="flex items-center justify-between gap-2 px-2 py-1.5 rounded-md text-sm font-medium text-gray-600 hover:bg-gray-50 cursor-pointer">
                            <div className="flex items-center gap-2">
                                <GitBranch className="w-4 h-4" />
                                <span>Workflows</span>
                            </div>
                            <ChevronRight className="w-3 h-3" />
                        </div>
                    </div>

                    <div className="mt-4 mb-2">
                        <div className="flex items-center justify-between px-2 py-1.5 text-sm font-medium text-gray-600 hover:bg-gray-50 cursor-pointer rounded-md">
                            <div className="flex items-center gap-2">
                                <Star className="w-4 h-4" />
                                <span>Quick Access</span>
                            </div>
                            <Plus className="w-3 h-3" />
                        </div>
                        <div className="space-y-0.5 mt-1">
                            <div className="flex items-center gap-2 px-2 py-1.5 rounded-md text-sm font-medium text-gray-600 hover:bg-gray-50 cursor-pointer pl-6">
                                <span>Urgent Cases</span>
                            </div>
                            <div className="flex items-center gap-2 px-2 py-1.5 rounded-md text-sm font-medium text-gray-600 hover:bg-gray-50 cursor-pointer pl-6">
                                <span>My Reviews</span>
                            </div>
                            <div className="flex items-center gap-2 px-2 py-1.5 rounded-md text-sm font-medium text-gray-600 hover:bg-gray-50 cursor-pointer pl-6">
                                <span>Trending Signals</span>
                            </div>
                            <div className="flex items-center gap-2 px-2 py-1.5 rounded-md text-sm font-medium text-gray-600 hover:bg-gray-50 cursor-pointer pl-6">
                                <span>Bookmarked</span>
                            </div>
                        </div>
                    </div>

                    <div className="mt-4">
                        <div className="flex items-center justify-between px-2 py-1.5 text-sm font-medium text-gray-600 hover:bg-gray-50 cursor-pointer rounded-md">
                            <div className="flex items-center gap-2">
                                <Database className="w-4 h-4" />
                                <span>Database</span>
                            </div>
                            <Plus className="w-3 h-3" />
                        </div>
                        <div className="space-y-0.5 mt-1">
                            <div className="flex items-center gap-2 px-2 py-1.5 rounded-md text-sm font-medium text-gray-600 hover:bg-gray-50 cursor-pointer pl-6">
                                <FileText className="w-4 h-4" />
                                <span>Products</span>
                            </div>
                            <div className="flex items-center gap-2 px-2 py-1.5 rounded-md text-sm font-medium text-gray-600 hover:bg-gray-50 cursor-pointer pl-6">
                                <Users className="w-4 h-4" />
                                <span>Patients</span>
                            </div>
                            <div className="flex items-center gap-2 px-2 py-1.5 rounded-md text-sm font-medium text-gray-600 hover:bg-gray-50 cursor-pointer pl-6">
                                <Building2 className="w-4 h-4" />
                                <span>Healthcare Providers</span>
                            </div>
                        </div>
                    </div>
                </nav>

                {/* Bottom Section */}
                <div className="px-2 pb-3 space-y-0.5">
                    <div className="flex items-center gap-2 px-2 py-1.5 rounded-md text-sm font-medium text-gray-600 hover:bg-gray-50 cursor-pointer">
                        <HelpCircle className="w-4 h-4" />
                        <span>Help & Support</span>
                    </div>
                    <div className="flex items-center gap-2 px-2 py-1.5 rounded-md text-sm font-medium text-gray-600 hover:bg-gray-50 cursor-pointer">
                        <FileText className="w-4 h-4" />
                        <span>Documentation</span>
                    </div>
                    <div className="flex items-center gap-2 px-2 py-1.5 rounded-md text-sm font-medium text-gray-600 hover:bg-gray-50 cursor-pointer">
                        <Settings className="w-4 h-4" />
                        <span>Settings</span>
                    </div>
                </div>

                {/* User Profile */}
                <div className="px-4 py-3 border-t border-gray-200">
                    <div className="flex items-center gap-2">
                        <img src="https://i.pravatar.cc/150?img=47" alt="User" className="w-8 h-8 rounded-full" />
                        <div className="flex-1 min-w-0">
                            <div className="text-sm font-medium text-gray-900">Dr. Sarah Mitchell</div>
                            <div className="text-xs text-gray-500 truncate">Safety Reviewer</div>
                        </div>
                        <MoreHorizontal className="w-4 h-4 text-gray-400" />
                    </div>
                </div>
            </aside>

            {/* Main Content */}
            <div className="flex-1 flex flex-col overflow-hidden">
                {/* Top Bar */}
                <header className="bg-white px-6 py-3 flex items-center justify-between" style={{ borderBottom: '1px solid #e5e7eb' }}>
                    <div className="flex items-center gap-3">
                        <AlertTriangle className="w-5 h-5 text-gray-400" />
                        <h1 className="text-lg font-semibold text-gray-900">Adverse Event Reports</h1>
                        <span className="text-sm text-gray-500">• 342 active cases</span>
                    </div>
                    <div className="flex items-center gap-3">
                        <div className="flex items-center gap-2">
                            <img src="https://i.pravatar.cc/150?img=45" alt="" className="w-7 h-7 rounded-full border-2 border-white -mr-2" />
                            <img src="https://i.pravatar.cc/150?img=27" alt="" className="w-7 h-7 rounded-full border-2 border-white -mr-2" />
                            <img src="https://i.pravatar.cc/150?img=68" alt="" className="w-7 h-7 rounded-full border-2 border-white -mr-2" />
                            <div className="w-7 h-7 rounded-full bg-gray-200 flex items-center justify-center text-xs font-medium text-gray-600">+12</div>
                        </div>
                        <button className="px-3 py-1.5 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 flex items-center gap-1.5">
                            <Calendar className="w-4 h-4" />
                            Export Reports
                        </button>
                        <button className="px-3 py-1.5 text-sm font-medium text-white rounded-md flex items-center gap-1.5 transition-colors" style={{ backgroundColor: '#073d44' }}
                            onMouseEnter={(e) => e.target.style.backgroundColor = '#0a5c66'}
                            onMouseLeave={(e) => e.target.style.backgroundColor = '#073d44'}>
                            <Plus className="w-4 h-4" />
                            New Case Report
                        </button>
                    </div>
                </header>

                {/* Main Content Area */}
                <main className="flex-1 overflow-y-auto">
                    {/* Metrics */}
                    <div className="px-6 py-6 grid grid-cols-6 gap-4">
                        <div className="bg-white rounded-lg border border-gray-200 p-4">
                            <div className="flex items-center gap-2 mb-2">
                                <FileText className="w-4 h-4 text-gray-400" />
                                <span className="text-sm text-gray-600">Total Cases</span>
                            </div>
                            <div className="flex items-end justify-between">
                                <div>
                                    <div className="text-2xl font-semibold text-gray-900">156</div>
                                    <div className="text-xs text-green-600">↑ 12% from last week</div>
                                </div>
                            </div>
                        </div>

                        <div className="bg-white rounded-lg border border-gray-200 p-4">
                            <div className="flex items-center gap-2 mb-2">
                                <Clock className="w-4 h-4 text-gray-400" />
                                <span className="text-sm text-gray-600">Pending Follow-ups</span>
                            </div>
                            <div className="flex items-end justify-between">
                                <div>
                                    <div className="text-2xl font-semibold text-gray-900">23</div>
                                    <div className="text-xs text-red-600">↓ 5% from last week</div>
                                </div>
                            </div>
                        </div>

                        <div className="bg-white rounded-lg border border-gray-200 p-4">
                            <div className="flex items-center gap-2 mb-2">
                                <CheckSquare className="w-4 h-4 text-gray-400" />
                                <span className="text-sm text-gray-600">Completed Today</span>
                            </div>
                            <div className="flex items-end justify-between">
                                <div>
                                    <div className="text-2xl font-semibold text-gray-900">12</div>
                                    <div className="text-xs text-green-600">↑ 8% from last week</div>
                                </div>
                            </div>
                        </div>

                        <div className="bg-white rounded-lg border border-gray-200 p-4">
                            <div className="flex items-center gap-2 mb-2">
                                <AlertTriangle className="w-4 h-4 text-gray-400" />
                                <span className="text-sm text-gray-600">Escalated</span>
                            </div>
                            <div className="flex items-end justify-between">
                                <div>
                                    <div className="text-2xl font-semibold text-gray-900">5</div>
                                </div>
                            </div>
                        </div>

                        <div className="bg-white rounded-lg border border-gray-200 p-4">
                            <div className="flex items-center gap-2 mb-2">
                                <Activity className="w-4 h-4 text-gray-400" />
                                <span className="text-sm text-gray-600">Avg. Completeness</span>
                            </div>
                            <div className="flex items-end justify-between">
                                <div>
                                    <div className="text-2xl font-semibold text-gray-900">78%</div>
                                </div>
                            </div>
                        </div>

                        <div className="bg-white rounded-lg border border-gray-200 p-4">
                            <div className="flex items-center gap-2 mb-2">
                                <TrendingUp className="w-4 h-4 text-gray-400" />
                                <span className="text-sm text-gray-600">Avg. Confidence</span>
                            </div>
                            <div className="flex items-end justify-between">
                                <div>
                                    <div className="text-2xl font-semibold text-gray-900">82%</div>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Table Controls */}
                    <div className="px-6 pb-4">
                        <div className="bg-white rounded-lg border border-gray-200">
                            <div className="px-4 py-3 flex items-center justify-between border-b border-gray-200">
                                <div className="flex items-center gap-2">
                                    <button
                                        onClick={() => setViewMode('table')}
                                        className={`flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium rounded-md ${viewMode === 'table' ? 'bg-gray-100 text-gray-900' : 'text-gray-600 hover:bg-gray-50'}`}
                                    >
                                        <Columns className="w-4 h-4" />
                                        Table
                                    </button>
                                    <button
                                        onClick={() => setViewMode('board')}
                                        className={`flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium rounded-md ${viewMode === 'board' ? 'bg-gray-100 text-gray-900' : 'text-gray-600 hover:bg-gray-50'}`}
                                    >
                                        <Grid3x3 className="w-4 h-4" />
                                        Board
                                    </button>
                                    <button className="flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium text-gray-600 hover:bg-gray-50 rounded-md">
                                        <List className="w-4 h-4" />
                                        List
                                    </button>
                                </div>
                                <div className="flex items-center gap-2">
                                    <button className="flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50">
                                        <Search className="w-4 h-4" />
                                        Search
                                    </button>
                                    <button className="flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50">
                                        <Eye className="w-4 h-4" />
                                        Filter
                                    </button>
                                    <button className="flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50">
                                        <Download className="w-4 h-4" />
                                        Export
                                    </button>
                                    <button className="flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50">
                                        Settings
                                        <ChevronDown className="w-4 h-4" />
                                    </button>
                                </div>
                            </div>

                            {/* Filter Bar */}
                            <div className="px-4 py-3 flex items-center gap-2 border-b border-gray-200 bg-gray-50">
                                <button className="flex items-center gap-1.5 px-2.5 py-1 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50">
                                    <AlertTriangle className="w-3.5 h-3.5" />
                                    Severity
                                    <ChevronDown className="w-3.5 h-3.5" />
                                </button>
                                <button className="flex items-center gap-1.5 px-2.5 py-1 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50">
                                    <FileText className="w-3.5 h-3.5" />
                                    Status
                                    <ChevronDown className="w-3.5 h-3.5" />
                                </button>
                                <button className="flex items-center gap-1.5 px-2.5 py-1 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50">
                                    <User className="w-3.5 h-3.5" />
                                    Reporter
                                    <ChevronDown className="w-3.5 h-3.5" />
                                </button>
                                <button className="flex items-center gap-1.5 px-2.5 py-1 text-sm font-medium text-gray-600 hover:bg-gray-100 rounded-md">
                                    <Plus className="w-3.5 h-3.5" />
                                    Add filter
                                </button>
                            </div>

                            {/* Table */}
                            <div className="overflow-x-auto">
                                <table className="w-full">
                                    <thead className="bg-gray-50 border-b border-gray-200">
                                        <tr>
                                            <th className="px-4 py-2 text-left">
                                                <span className="text-xs font-medium text-gray-500 uppercase">Case ID</span>
                                            </th>
                                            <th className="px-4 py-2 text-left">
                                                <span className="text-xs font-medium text-gray-500 uppercase">Patient</span>
                                            </th>
                                            <th className="px-4 py-2 text-left">
                                                <span className="text-xs font-medium text-gray-500 uppercase">Drug</span>
                                            </th>
                                            <th className="px-4 py-2 text-left">
                                                <span className="text-xs font-medium text-gray-500 uppercase">Event</span>
                                            </th>
                                            <th className="px-4 py-2 text-left">
                                                <span className="text-xs font-medium text-gray-500 uppercase">Severity</span>
                                            </th>
                                            <th className="px-4 py-2 text-left">
                                                <span className="text-xs font-medium text-gray-500 uppercase">Status</span>
                                            </th>
                                            <th className="px-4 py-2 text-left">
                                                <span className="text-xs font-medium text-gray-500 uppercase">Completeness</span>
                                            </th>
                                            <th className="px-4 py-2 text-left">
                                                <span className="text-xs font-medium text-gray-500 uppercase">Confidence</span>
                                            </th>
                                            <th className="px-4 py-2">
                                                <span className="text-xs font-medium text-gray-500 uppercase">Actions</span>
                                            </th>
                                        </tr>
                                    </thead>
                                    <tbody className="divide-y divide-gray-200 bg-white">
                                        {caseReports.map((report, index) => {
                                            const severityColor = getSeverityColor(report.severity);
                                            const statusColor = getStatusColor(report.status);
                                            return (
                                                <tr key={index} className="hover:bg-gray-50">
                                                    <td className="px-4 py-3">
                                                        <span className="text-sm font-medium text-blue-600">{report.id}</span>
                                                    </td>
                                                    <td className="px-4 py-3">
                                                        <div>
                                                            <div className="text-sm font-medium text-gray-900">{report.patient}</div>
                                                            <div className="text-xs text-gray-500">{report.location}</div>
                                                        </div>
                                                    </td>
                                                    <td className="px-4 py-3">
                                                        <span className="text-sm text-gray-700">{report.drug}</span>
                                                    </td>
                                                    <td className="px-4 py-3">
                                                        <span className="text-sm text-gray-700">{report.event}</span>
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
                                                            <div className="flex-1 bg-gray-200 rounded-full h-1.5">
                                                                <div
                                                                    className="h-1.5 rounded-full"
                                                                    style={{
                                                                        width: `${report.completeness}%`,
                                                                        backgroundColor: '#059669'
                                                                    }}
                                                                ></div>
                                                            </div>
                                                            <span className="text-xs text-gray-600 w-8">{report.completeness}%</span>
                                                        </div>
                                                    </td>
                                                    <td className="px-4 py-3">
                                                        <span className="text-sm font-medium" style={{ color: '#059669' }}>{report.confidence}%</span>
                                                    </td>
                                                    <td className="px-4 py-3">
                                                        <div className="flex items-center gap-2">
                                                            <button className="text-gray-400 hover:text-gray-600">
                                                                <Eye className="w-4 h-4" />
                                                            </button>
                                                            <button className="text-gray-400 hover:text-gray-600">
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
                </main>
            </div>
        </div>
    );
};

export default Dashboard;