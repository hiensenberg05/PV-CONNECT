import React from 'react';
import { X, User, MapPin, Pill, FileText, Activity, Calendar, Clock, AlertTriangle, Shield, CheckCircle, Phone, Stethoscope, Heart, ClipboardList } from 'lucide-react';
import useThemeStore from '../store/themeStore';

const CaseDetailsModal = ({ isOpen, onClose, caseData, rawCaseData }) => {
    const { darkMode } = useThemeStore();

    // Theme colors matching AddCaseReportModal
    const theme = {
        bg: darkMode ? '#111827' : '#ffffff',
        bgSecondary: darkMode ? '#1f2937' : '#f9fafb',
        text: darkMode ? '#f9fafb' : '#111827',
        textSecondary: darkMode ? '#9ca3af' : '#6b7280',
        border: darkMode ? '#374151' : '#e5e7eb',
        labelText: darkMode ? '#d1d5db' : '#374151',
        hoverBg: darkMode ? '#374151' : '#f3f4f6',
        accent: '#073d44',
    };

    const getSeverityColor = (severity) => {
        const sev = typeof severity === 'string' ? severity : 'Unknown';
        if (darkMode) {
            switch (sev) {
                case 'Severe': case 'hospitalized': case 'death': return { bg: '#374151', text: '#f87171' };
                case 'Moderate': case 'affected_daily_activity': return { bg: '#374151', text: '#fbbf24' };
                case 'Mild': case 'no_daily_activity_effect': return { bg: '#374151', text: '#9ca3af' };
                default: return { bg: '#374151', text: '#d1d5db' };
            }
        }
        switch (sev) {
            case 'Severe': case 'hospitalized': case 'death': return { bg: '#fef2f2', text: '#dc2626' };
            case 'Moderate': case 'affected_daily_activity': return { bg: '#fffbeb', text: '#d97706' };
            case 'Mild': case 'no_daily_activity_effect': return { bg: '#f9fafb', text: '#6b7280' };
            default: return { bg: '#f3f4f6', text: '#374151' };
        }
    };

    const getStatusColor = (status) => {
        if (darkMode) {
            switch (status) {
                case 'Pending': return { bg: '#374151', text: '#a5b4fc' };
                case 'In Progress': return { bg: '#374151', text: '#60a5fa' };
                case 'Escalated': return { bg: '#374151', text: '#f87171' };
                case 'Complete': return { bg: '#374151', text: '#4ade80' };
                default: return { bg: '#374151', text: '#d1d5db' };
            }
        }
        switch (status) {
            case 'Pending': return { bg: '#eef2ff', text: '#6366f1' };
            case 'In Progress': return { bg: '#eff6ff', text: '#3b82f6' };
            case 'Escalated': return { bg: '#fef2f2', text: '#dc2626' };
            case 'Complete': return { bg: '#f0fdf4', text: '#16a34a' };
            default: return { bg: '#f3f4f6', text: '#374151' };
        }
    };

    if (!isOpen || !caseData) return null;

    // Extract full data from rawCaseData if available, fallback to caseData
    const fullData = rawCaseData?.data || {};
    const patientDetails = fullData.patient_details || {};
    const medicineDetails = fullData.medicine_details || [];
    const reactionDetails = fullData.reaction_details || {};
    const severity = fullData.severity || [];
    const description = fullData.description || '';
    const managementAction = fullData.management_action || '';
    const pastDiseaseHistory = fullData.past_disease_history || '';

    const statusColor = getStatusColor(caseData.status);

    // Helper to render a detail row
    const DetailRow = ({ icon: Icon, label, value, valueColor }) => (
        <div className="flex items-start gap-3 py-2">
            <div className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0"
                style={{ backgroundColor: darkMode ? '#374151' : '#f3f4f6' }}>
                <Icon className="w-4 h-4" style={{ color: theme.textSecondary }} />
            </div>
            <div className="flex-1 min-w-0">
                <div className="text-xs font-medium uppercase tracking-wide" style={{ color: theme.textSecondary }}>
                    {label}
                </div>
                <div className="text-sm font-medium mt-0.5" style={{ color: valueColor || theme.text }}>
                    {value || 'Not provided'}
                </div>
            </div>
        </div>
    );

    // Simple detail item for grids
    const DetailItem = ({ label, value }) => (
        <div className="py-1">
            <div className="text-xs" style={{ color: theme.textSecondary }}>{label}</div>
            <div className="text-sm font-medium" style={{ color: theme.text }}>{value || '—'}</div>
        </div>
    );

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
            {/* Backdrop */}
            <div
                className="absolute inset-0"
                style={{ backgroundColor: 'rgba(0, 0, 0, 0.6)' }}
                onClick={onClose}
            />

            {/* Modal */}
            <div
                className="relative rounded-lg shadow-2xl w-full max-w-3xl mx-4 overflow-hidden max-h-[90vh] flex flex-col"
                style={{ backgroundColor: theme.bg }}
            >
                {/* Header */}
                <div
                    className="px-5 py-4 flex items-center justify-between flex-shrink-0"
                    style={{ borderBottom: `1px solid ${theme.border}` }}
                >
                    <div className="flex items-center gap-3">
                        <div
                            className="w-10 h-10 rounded-lg flex items-center justify-center"
                            style={{ backgroundColor: theme.accent }}
                        >
                            <FileText className="w-5 h-5 text-white" />
                        </div>
                        <div>
                            <h2 className="text-lg font-semibold" style={{ color: theme.text }}>
                                Case Details
                            </h2>
                            <p className="text-sm" style={{ color: '#3b82f6' }}>
                                {rawCaseData?.case_id || caseData.id}
                            </p>
                        </div>
                    </div>
                    <div className="flex items-center gap-3">
                        <span
                            className="inline-flex items-center px-3 py-1.5 text-sm font-medium rounded-md gap-1.5"
                            style={{ backgroundColor: statusColor.bg, color: statusColor.text }}
                        >
                            {caseData.status || 'Pending'}
                        </span>
                        <button
                            onClick={onClose}
                            className="w-8 h-8 rounded-md flex items-center justify-center transition-colors"
                            style={{ color: theme.textSecondary }}
                            onMouseEnter={(e) => e.currentTarget.style.backgroundColor = theme.hoverBg}
                            onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
                        >
                            <X className="w-5 h-5" />
                        </button>
                    </div>
                </div>

                {/* Content */}
                <div className="flex-1 overflow-y-auto p-5" style={{ backgroundColor: theme.bgSecondary }}>

                    {/* Patient Information */}
                    <div className="rounded-lg p-4 mb-4" style={{ backgroundColor: theme.bg, border: `1px solid ${theme.border}` }}>
                        <h3 className="text-xs font-semibold uppercase tracking-wider mb-3 flex items-center gap-2" style={{ color: theme.textSecondary }}>
                            <User className="w-4 h-4" />
                            Patient Information
                        </h3>
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                            <DetailItem label="Name" value={patientDetails.name || caseData.patient} />
                            <DetailItem label="Gender" value={patientDetails.gender} />
                            <DetailItem label="Age" value={patientDetails.age_value ? `${patientDetails.age_value} ${patientDetails.age_unit || 'years'}` : null} />
                            <DetailItem label="Phone" value={rawCaseData?.patient_phone} />
                        </div>
                        <div className="grid grid-cols-2 gap-4 mt-2">
                            <DetailItem label="Reporter Type" value={rawCaseData?.reporter_type} />
                            <DetailItem label="Location" value={caseData.location} />
                        </div>
                    </div>

                    {/* Medicine Details */}
                    <div className="rounded-lg p-4 mb-4" style={{ backgroundColor: theme.bg, border: `1px solid ${theme.border}` }}>
                        <h3 className="text-xs font-semibold uppercase tracking-wider mb-3 flex items-center gap-2" style={{ color: theme.textSecondary }}>
                            <Pill className="w-4 h-4" />
                            Medicine Details
                        </h3>
                        {medicineDetails.length > 0 ? (
                            medicineDetails.map((med, idx) => (
                                <div key={idx} className="p-3 rounded-lg mb-2" style={{ backgroundColor: theme.bgSecondary }}>
                                    <div className="font-medium text-sm mb-2" style={{ color: theme.text }}>
                                        {med.name || 'Unknown Medicine'} {idx > 0 ? `(#${idx + 1})` : ''}
                                    </div>
                                    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                                        <DetailItem label="Quantity" value={med.quantity_taken} />
                                        <DetailItem label="Dosage Form" value={med.dosage_form} />
                                        <DetailItem label="Start Date" value={med.start_date} />
                                        <DetailItem label="Stop Date" value={med.stop_date} />
                                    </div>
                                    <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mt-2">
                                        <DetailItem label="Expiry Date" value={med.expiry_date} />
                                        <DetailItem label="Advised By" value={med.advised_by} />
                                        <DetailItem label="Self Medicated" value={med.self_medicated === true ? 'Yes' : med.self_medicated === false ? 'No' : null} />
                                        <DetailItem label="Reason" value={med.reason_for_medicine} />
                                    </div>
                                </div>
                            ))
                        ) : (
                            <div className="text-sm" style={{ color: theme.textSecondary }}>
                                {caseData.drug ? caseData.drug : 'No medicine information available'}
                            </div>
                        )}
                    </div>

                    {/* Reaction / Side Effect Details */}
                    <div className="rounded-lg p-4 mb-4" style={{ backgroundColor: theme.bg, border: `1px solid ${theme.border}` }}>
                        <h3 className="text-xs font-semibold uppercase tracking-wider mb-3 flex items-center gap-2" style={{ color: theme.textSecondary }}>
                            <AlertTriangle className="w-4 h-4" />
                            Reaction / Side Effect
                        </h3>
                        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                            <DetailItem label="Start Date" value={reactionDetails.start_date} />
                            <DetailItem label="Still Continuing?" value={reactionDetails.continuing === true ? 'Yes' : reactionDetails.continuing === false ? 'No' : null} />
                            <DetailItem label="Stop Date" value={reactionDetails.stop_date} />
                        </div>
                        <div className="mt-3">
                            <div className="text-xs mb-1" style={{ color: theme.textSecondary }}>Description</div>
                            <div className="text-sm p-3 rounded" style={{ backgroundColor: theme.bgSecondary, color: theme.text }}>
                                {description || caseData.event || 'No description provided'}
                            </div>
                        </div>
                    </div>

                    {/* Severity */}
                    <div className="rounded-lg p-4 mb-4" style={{ backgroundColor: theme.bg, border: `1px solid ${theme.border}` }}>
                        <h3 className="text-xs font-semibold uppercase tracking-wider mb-3 flex items-center gap-2" style={{ color: theme.textSecondary }}>
                            <Activity className="w-4 h-4" />
                            Severity
                        </h3>
                        <div className="flex flex-wrap gap-2">
                            {severity.length > 0 ? (
                                severity.map((sev, idx) => {
                                    const sevColor = getSeverityColor(sev);
                                    return (
                                        <span
                                            key={idx}
                                            className="inline-flex items-center px-3 py-1.5 text-sm font-medium rounded-md"
                                            style={{ backgroundColor: sevColor.bg, color: sevColor.text }}
                                        >
                                            {sev.replace(/_/g, ' ')}
                                        </span>
                                    );
                                })
                            ) : (
                                <span className="text-sm" style={{ color: theme.textSecondary }}>
                                    {caseData.severity || 'Not specified'}
                                </span>
                            )}
                        </div>
                    </div>

                    {/* Medical History & Management */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                        <div className="rounded-lg p-4" style={{ backgroundColor: theme.bg, border: `1px solid ${theme.border}` }}>
                            <h3 className="text-xs font-semibold uppercase tracking-wider mb-3 flex items-center gap-2" style={{ color: theme.textSecondary }}>
                                <Heart className="w-4 h-4" />
                                Past Disease History
                            </h3>
                            <div className="text-sm" style={{ color: theme.text }}>
                                {pastDiseaseHistory || 'Not provided'}
                            </div>
                        </div>
                        <div className="rounded-lg p-4" style={{ backgroundColor: theme.bg, border: `1px solid ${theme.border}` }}>
                            <h3 className="text-xs font-semibold uppercase tracking-wider mb-3 flex items-center gap-2" style={{ color: theme.textSecondary }}>
                                <Stethoscope className="w-4 h-4" />
                                Management Action
                            </h3>
                            <div className="text-sm" style={{ color: theme.text }}>
                                {managementAction || 'Not provided'}
                            </div>
                        </div>
                    </div>

                    {/* Analytics Scores */}
                    <div className="rounded-lg p-4" style={{ backgroundColor: theme.bg, border: `1px solid ${theme.border}` }}>
                        <h3 className="text-xs font-semibold uppercase tracking-wider mb-3 flex items-center gap-2" style={{ color: theme.textSecondary }}>
                            <ClipboardList className="w-4 h-4" />
                            Analytics Scores
                        </h3>
                        <div className="grid grid-cols-2 gap-4">
                            {/* Completeness */}
                            <div className="p-3 rounded-lg" style={{ backgroundColor: theme.bgSecondary }}>
                                <div className="flex items-center justify-between mb-2">
                                    <span className="text-xs font-medium" style={{ color: theme.textSecondary }}>Completeness</span>
                                    <span className="text-sm font-semibold" style={{ color: '#10b981' }}>{caseData.completeness || 0}%</span>
                                </div>
                                <div className="w-full rounded-full h-2" style={{ backgroundColor: darkMode ? '#374151' : '#e5e7eb' }}>
                                    <div
                                        className="h-2 rounded-full transition-all"
                                        style={{ width: `${caseData.completeness || 0}%`, backgroundColor: '#10b981' }}
                                    />
                                </div>
                            </div>

                            {/* Confidence */}
                            <div className="p-3 rounded-lg" style={{ backgroundColor: theme.bgSecondary }}>
                                <div className="flex items-center justify-between mb-2">
                                    <span className="text-xs font-medium" style={{ color: theme.textSecondary }}>Confidence</span>
                                    <span className="text-sm font-semibold" style={{ color: '#3b82f6' }}>{caseData.confidence || 0}%</span>
                                </div>
                                <div className="w-full rounded-full h-2" style={{ backgroundColor: darkMode ? '#374151' : '#e5e7eb' }}>
                                    <div
                                        className="h-2 rounded-full transition-all"
                                        style={{ width: `${caseData.confidence || 0}%`, backgroundColor: '#3b82f6' }}
                                    />
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Footer */}
                <div
                    className="px-5 py-3 flex items-center justify-between flex-shrink-0"
                    style={{ borderTop: `1px solid ${theme.border}`, backgroundColor: theme.bg }}
                >
                    <div className="text-xs" style={{ color: theme.textSecondary }}>
                        Created: {rawCaseData?.created_at ? new Date(rawCaseData.created_at).toLocaleString() : 'N/A'}
                    </div>
                    <button
                        onClick={onClose}
                        className="px-4 py-2 text-sm font-medium text-white rounded-md transition-colors"
                        style={{ backgroundColor: theme.accent }}
                        onMouseEnter={(e) => e.target.style.backgroundColor = '#0a5c66'}
                        onMouseLeave={(e) => e.target.style.backgroundColor = theme.accent}
                    >
                        Close
                    </button>
                </div>
            </div>
        </div>
    );
};

export default CaseDetailsModal;
