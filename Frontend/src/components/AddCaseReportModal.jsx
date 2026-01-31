import React, { useState } from 'react';
import { X, AlertTriangle, User, MapPin, Pill, FileText, Activity, Calendar, Clock, Heart, Stethoscope, Phone } from 'lucide-react';
import useThemeStore from '../store/themeStore';

const AddCaseReportModal = ({ isOpen, onClose, onAddCase }) => {
    const { darkMode } = useThemeStore();

    const [formData, setFormData] = useState({
        // Patient Details
        patientName: '',
        patientGender: '',
        patientAge: '',
        patientAgeUnit: 'years',
        patientPhone: '',
        // Medicine Details
        medicineName: '',
        medicineQuantity: '',
        medicineDosageForm: '',
        medicineStartDate: '',
        medicineStopDate: '',
        medicineExpiryDate: '',
        medicineReason: '',
        medicineAdvisedBy: '',
        selfMedicated: false,
        // Reaction Details
        reactionStartDate: '',
        reactionContinuing: false,
        reactionStopDate: '',
        description: '',
        // Severity & Other
        severity: [],
        managementAction: '',
        pastDiseaseHistory: '',
        status: 'Pending'
    });

    const [errors, setErrors] = useState({});

    const genderOptions = ['Male', 'Female', 'Other'];
    const ageUnitOptions = ['years', 'months', 'days'];
    const dosageFormOptions = ['Tablet', 'Capsule', 'Syrup', 'Injection', 'Cream', 'Drops', 'Inhaler', 'Other'];
    const severityOptions = [
        { value: 'no_daily_activity_effect', label: 'No effect on daily activity' },
        { value: 'affected_daily_activity', label: 'Affected daily activity' },
        { value: 'hospitalized', label: 'Hospitalized' },
        { value: 'life_threatening', label: 'Life threatening' },
        { value: 'death', label: 'Death' },
        { value: 'birth_defect', label: 'Birth defect' }
    ];
    const statusOptions = ['Pending', 'In Progress', 'Complete', 'Escalated'];

    // Theme colors
    const theme = {
        bg: darkMode ? '#111827' : '#ffffff',
        bgSecondary: darkMode ? '#1f2937' : '#f9fafb',
        text: darkMode ? '#f9fafb' : '#111827',
        textSecondary: darkMode ? '#9ca3af' : '#6b7280',
        border: darkMode ? '#374151' : '#e5e7eb',
        inputBg: darkMode ? '#1f2937' : '#ffffff',
        inputBorder: darkMode ? '#4b5563' : '#d1d5db',
        inputText: darkMode ? '#f9fafb' : '#111827',
        labelText: darkMode ? '#d1d5db' : '#374151',
        hoverBg: darkMode ? '#374151' : '#f3f4f6',
        cancelBg: darkMode ? '#374151' : '#ffffff',
        cancelText: darkMode ? '#d1d5db' : '#374151',
        cancelBorder: darkMode ? '#4b5563' : '#d1d5db',
        accent: '#073d44',
    };

    const handleChange = (e) => {
        const { name, value, type, checked } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: type === 'checkbox' ? checked : value
        }));
        if (errors[name]) {
            setErrors(prev => ({ ...prev, [name]: '' }));
        }
    };

    const handleSeverityChange = (value) => {
        setFormData(prev => ({
            ...prev,
            severity: prev.severity.includes(value)
                ? prev.severity.filter(s => s !== value)
                : [...prev.severity, value]
        }));
    };

    const validateForm = () => {
        const newErrors = {};
        if (!formData.patientName.trim()) newErrors.patientName = 'Patient name is required';
        if (!formData.medicineName.trim()) newErrors.medicineName = 'Medicine name is required';
        if (!formData.description.trim()) newErrors.description = 'Adverse event description is required';
        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        if (!validateForm()) return;

        // Build case object matching backend schema
        const newCase = {
            id: `AE-${new Date().getFullYear()}-${String(Math.floor(Math.random() * 900) + 100).padStart(3, '0')}`,
            patient: formData.patientName,
            location: 'Manual Entry',
            drug: formData.medicineName,
            event: formData.description,
            severity: formData.severity[0] || 'Unknown',
            status: formData.status,
            completeness: 0,
            confidence: 0,
            _raw: {
                case_id: `AE-${new Date().getFullYear()}-${String(Math.floor(Math.random() * 900) + 100).padStart(3, '0')}`,
                patient_phone: formData.patientPhone,
                reporter_type: 'manual',
                data: {
                    patient_details: {
                        name: formData.patientName,
                        gender: formData.patientGender || null,
                        age_value: formData.patientAge ? parseInt(formData.patientAge) : null,
                        age_unit: formData.patientAgeUnit
                    },
                    medicine_details: [{
                        name: formData.medicineName,
                        quantity_taken: formData.medicineQuantity || null,
                        dosage_form: formData.medicineDosageForm || null,
                        expiry_date: formData.medicineExpiryDate || null,
                        start_date: formData.medicineStartDate || null,
                        stop_date: formData.medicineStopDate || null,
                        reason_for_medicine: formData.medicineReason || null,
                        advised_by: formData.medicineAdvisedBy || null,
                        self_medicated: formData.selfMedicated
                    }],
                    reaction_details: {
                        start_date: formData.reactionStartDate || null,
                        continuing: formData.reactionContinuing,
                        stop_date: formData.reactionStopDate || null
                    },
                    severity: formData.severity,
                    description: formData.description,
                    management_action: formData.managementAction || null,
                    past_disease_history: formData.pastDiseaseHistory || null
                },
                created_at: new Date().toISOString()
            }
        };

        onAddCase(newCase);
        // Reset form
        setFormData({
            patientName: '', patientGender: '', patientAge: '', patientAgeUnit: 'years', patientPhone: '',
            medicineName: '', medicineQuantity: '', medicineDosageForm: '', medicineStartDate: '', medicineStopDate: '',
            medicineExpiryDate: '', medicineReason: '', medicineAdvisedBy: '', selfMedicated: false,
            reactionStartDate: '', reactionContinuing: false, reactionStopDate: '', description: '',
            severity: [], managementAction: '', pastDiseaseHistory: '', status: 'Pending'
        });
        onClose();
    };

    // Reusable input component
    const InputField = ({ icon: Icon, label, name, type = 'text', placeholder, required, ...props }) => (
        <div>
            <label className="flex items-center gap-2 text-sm font-medium mb-1.5" style={{ color: theme.labelText }}>
                {Icon && <Icon className="w-3.5 h-3.5" style={{ color: theme.textSecondary }} />}
                {label} {required && <span style={{ color: '#ef4444' }}>*</span>}
            </label>
            <input
                type={type}
                name={name}
                value={formData[name]}
                onChange={handleChange}
                placeholder={placeholder}
                className="w-full px-3 py-2 text-sm rounded-md outline-none transition-all"
                style={{
                    backgroundColor: theme.inputBg,
                    border: errors[name] ? '1px solid #ef4444' : `1px solid ${theme.inputBorder}`,
                    color: theme.inputText
                }}
                {...props}
            />
            {errors[name] && (
                <p className="text-xs mt-1 flex items-center gap-1" style={{ color: '#ef4444' }}>
                    <AlertTriangle className="w-3 h-3" />{errors[name]}
                </p>
            )}
        </div>
    );

    // Reusable select component
    const SelectField = ({ icon: Icon, label, name, options, placeholder }) => (
        <div>
            <label className="flex items-center gap-2 text-sm font-medium mb-1.5" style={{ color: theme.labelText }}>
                {Icon && <Icon className="w-3.5 h-3.5" style={{ color: theme.textSecondary }} />}
                {label}
            </label>
            <select
                name={name}
                value={formData[name]}
                onChange={handleChange}
                className="w-full px-3 py-2 text-sm rounded-md outline-none transition-all"
                style={{
                    backgroundColor: theme.inputBg,
                    border: `1px solid ${theme.inputBorder}`,
                    color: theme.inputText
                }}
            >
                <option value="">{placeholder || 'Select...'}</option>
                {options.map(opt => (
                    <option key={opt} value={opt}>{opt}</option>
                ))}
            </select>
        </div>
    );

    if (!isOpen) return null;

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
                className="relative rounded-lg shadow-2xl w-full max-w-3xl mx-4 max-h-[90vh] flex flex-col overflow-hidden"
                style={{ backgroundColor: theme.bg }}
            >
                {/* Header */}
                <div
                    className="px-5 py-3 flex items-center justify-between flex-shrink-0"
                    style={{ borderBottom: `1px solid ${theme.border}` }}
                >
                    <div className="flex items-center gap-2.5">
                        <div
                            className="w-9 h-9 rounded-lg flex items-center justify-center"
                            style={{ backgroundColor: theme.accent }}
                        >
                            <FileText className="w-4 h-4 text-white" />
                        </div>
                        <div>
                            <h2 className="text-base font-semibold" style={{ color: theme.text }}>
                                New Case Report
                            </h2>
                            <p className="text-xs" style={{ color: theme.textSecondary }}>
                                Report an adverse event case
                            </p>
                        </div>
                    </div>
                    <button
                        onClick={onClose}
                        className="w-7 h-7 rounded-md flex items-center justify-center transition-colors"
                        style={{ color: theme.textSecondary }}
                        onMouseEnter={(e) => e.currentTarget.style.backgroundColor = theme.hoverBg}
                        onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
                    >
                        <X className="w-4 h-4" />
                    </button>
                </div>

                {/* Scrollable Form */}
                <form onSubmit={handleSubmit} className="flex-1 overflow-y-auto p-5" style={{ backgroundColor: theme.bgSecondary }}>
                    <div className="space-y-5">

                        {/* Patient Information Section */}
                        <div className="rounded-lg p-4" style={{ backgroundColor: theme.bg, border: `1px solid ${theme.border}` }}>
                            <h3 className="text-xs font-semibold uppercase tracking-wider mb-3 flex items-center gap-2" style={{ color: theme.textSecondary }}>
                                <User className="w-4 h-4" /> Patient Information
                            </h3>
                            <div className="grid grid-cols-2 gap-3">
                                <InputField icon={User} label="Patient Name" name="patientName" placeholder="Enter patient name" required />
                                <div className="grid grid-cols-2 gap-2">
                                    <SelectField label="Gender" name="patientGender" options={genderOptions} placeholder="Select" />
                                    <div className="flex gap-2">
                                        <div className="flex-1">
                                            <label className="text-sm font-medium mb-1.5 block" style={{ color: theme.labelText }}>Age</label>
                                            <input
                                                type="number"
                                                name="patientAge"
                                                value={formData.patientAge}
                                                onChange={handleChange}
                                                placeholder="Age"
                                                className="w-full px-3 py-2 text-sm rounded-md outline-none"
                                                style={{ backgroundColor: theme.inputBg, border: `1px solid ${theme.inputBorder}`, color: theme.inputText }}
                                            />
                                        </div>
                                        <div className="w-20">
                                            <label className="text-sm font-medium mb-1.5 block" style={{ color: theme.labelText }}>Unit</label>
                                            <select
                                                name="patientAgeUnit"
                                                value={formData.patientAgeUnit}
                                                onChange={handleChange}
                                                className="w-full px-2 py-2 text-sm rounded-md"
                                                style={{ backgroundColor: theme.inputBg, border: `1px solid ${theme.inputBorder}`, color: theme.inputText }}
                                            >
                                                {ageUnitOptions.map(u => <option key={u} value={u}>{u}</option>)}
                                            </select>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div className="mt-3">
                                <InputField icon={Phone} label="Patient Phone" name="patientPhone" placeholder="+91XXXXXXXXXX" />
                            </div>
                        </div>

                        {/* Medicine Details Section */}
                        <div className="rounded-lg p-4" style={{ backgroundColor: theme.bg, border: `1px solid ${theme.border}` }}>
                            <h3 className="text-xs font-semibold uppercase tracking-wider mb-3 flex items-center gap-2" style={{ color: theme.textSecondary }}>
                                <Pill className="w-4 h-4" /> Medicine Details
                            </h3>
                            <div className="grid grid-cols-2 gap-3">
                                <InputField icon={Pill} label="Medicine Name" name="medicineName" placeholder="e.g., Paracetamol" required />
                                <div className="grid grid-cols-2 gap-2">
                                    <InputField label="Quantity" name="medicineQuantity" placeholder="e.g., 2 tablets" />
                                    <SelectField label="Dosage Form" name="medicineDosageForm" options={dosageFormOptions} placeholder="Select" />
                                </div>
                            </div>
                            <div className="grid grid-cols-3 gap-3 mt-3">
                                <InputField icon={Calendar} label="Start Date" name="medicineStartDate" type="date" />
                                <InputField icon={Calendar} label="Stop Date" name="medicineStopDate" type="date" />
                                <InputField icon={Calendar} label="Expiry Date" name="medicineExpiryDate" type="date" />
                            </div>
                            <div className="grid grid-cols-2 gap-3 mt-3">
                                <InputField label="Reason for Medicine" name="medicineReason" placeholder="Why was medicine taken?" />
                                <InputField label="Advised By" name="medicineAdvisedBy" placeholder="Doctor/Self/Pharmacist" />
                            </div>
                            <div className="mt-3 flex items-center gap-2">
                                <input
                                    type="checkbox"
                                    name="selfMedicated"
                                    checked={formData.selfMedicated}
                                    onChange={handleChange}
                                    className="w-4 h-4 rounded"
                                />
                                <label className="text-sm" style={{ color: theme.labelText }}>Self Medicated</label>
                            </div>
                        </div>

                        {/* Reaction Details Section */}
                        <div className="rounded-lg p-4" style={{ backgroundColor: theme.bg, border: `1px solid ${theme.border}` }}>
                            <h3 className="text-xs font-semibold uppercase tracking-wider mb-3 flex items-center gap-2" style={{ color: theme.textSecondary }}>
                                <AlertTriangle className="w-4 h-4" /> Reaction / Adverse Event
                            </h3>
                            <div className="grid grid-cols-3 gap-3">
                                <InputField icon={Calendar} label="Reaction Start Date" name="reactionStartDate" type="date" />
                                <InputField icon={Calendar} label="Reaction Stop Date" name="reactionStopDate" type="date" />
                                <div className="flex items-end gap-2 pb-2">
                                    <input
                                        type="checkbox"
                                        name="reactionContinuing"
                                        checked={formData.reactionContinuing}
                                        onChange={handleChange}
                                        className="w-4 h-4 rounded"
                                    />
                                    <label className="text-sm" style={{ color: theme.labelText }}>Still Continuing</label>
                                </div>
                            </div>
                            <div className="mt-3">
                                <label className="flex items-center gap-2 text-sm font-medium mb-1.5" style={{ color: theme.labelText }}>
                                    <FileText className="w-3.5 h-3.5" style={{ color: theme.textSecondary }} />
                                    Description <span style={{ color: '#ef4444' }}>*</span>
                                </label>
                                <textarea
                                    name="description"
                                    value={formData.description}
                                    onChange={handleChange}
                                    placeholder="Describe the adverse event in detail..."
                                    rows={3}
                                    className="w-full px-3 py-2 text-sm rounded-md outline-none resize-none"
                                    style={{
                                        backgroundColor: theme.inputBg,
                                        border: errors.description ? '1px solid #ef4444' : `1px solid ${theme.inputBorder}`,
                                        color: theme.inputText
                                    }}
                                />
                                {errors.description && (
                                    <p className="text-xs mt-1 flex items-center gap-1" style={{ color: '#ef4444' }}>
                                        <AlertTriangle className="w-3 h-3" />{errors.description}
                                    </p>
                                )}
                            </div>
                        </div>

                        {/* Severity Section */}
                        <div className="rounded-lg p-4" style={{ backgroundColor: theme.bg, border: `1px solid ${theme.border}` }}>
                            <h3 className="text-xs font-semibold uppercase tracking-wider mb-3 flex items-center gap-2" style={{ color: theme.textSecondary }}>
                                <Activity className="w-4 h-4" /> Severity (Select all that apply)
                            </h3>
                            <div className="grid grid-cols-2 gap-2">
                                {severityOptions.map(opt => (
                                    <label
                                        key={opt.value}
                                        className="flex items-center gap-2 p-2 rounded-md cursor-pointer transition-colors"
                                        style={{
                                            backgroundColor: formData.severity.includes(opt.value) ? (darkMode ? '#374151' : '#e0f2fe') : 'transparent',
                                            border: `1px solid ${formData.severity.includes(opt.value) ? theme.accent : theme.inputBorder}`
                                        }}
                                    >
                                        <input
                                            type="checkbox"
                                            checked={formData.severity.includes(opt.value)}
                                            onChange={() => handleSeverityChange(opt.value)}
                                            className="w-4 h-4 rounded"
                                        />
                                        <span className="text-sm" style={{ color: theme.text }}>{opt.label}</span>
                                    </label>
                                ))}
                            </div>
                        </div>

                        {/* Additional Information */}
                        <div className="rounded-lg p-4" style={{ backgroundColor: theme.bg, border: `1px solid ${theme.border}` }}>
                            <h3 className="text-xs font-semibold uppercase tracking-wider mb-3 flex items-center gap-2" style={{ color: theme.textSecondary }}>
                                <Heart className="w-4 h-4" /> Additional Information
                            </h3>
                            <div className="grid grid-cols-2 gap-3">
                                <div>
                                    <label className="text-sm font-medium mb-1.5 block" style={{ color: theme.labelText }}>
                                        <Stethoscope className="w-3.5 h-3.5 inline mr-1" style={{ color: theme.textSecondary }} />
                                        Management Action
                                    </label>
                                    <textarea
                                        name="managementAction"
                                        value={formData.managementAction}
                                        onChange={handleChange}
                                        placeholder="What action was taken?"
                                        rows={2}
                                        className="w-full px-3 py-2 text-sm rounded-md outline-none resize-none"
                                        style={{ backgroundColor: theme.inputBg, border: `1px solid ${theme.inputBorder}`, color: theme.inputText }}
                                    />
                                </div>
                                <div>
                                    <label className="text-sm font-medium mb-1.5 block" style={{ color: theme.labelText }}>
                                        <Heart className="w-3.5 h-3.5 inline mr-1" style={{ color: theme.textSecondary }} />
                                        Past Disease History
                                    </label>
                                    <textarea
                                        name="pastDiseaseHistory"
                                        value={formData.pastDiseaseHistory}
                                        onChange={handleChange}
                                        placeholder="Any relevant medical history?"
                                        rows={2}
                                        className="w-full px-3 py-2 text-sm rounded-md outline-none resize-none"
                                        style={{ backgroundColor: theme.inputBg, border: `1px solid ${theme.inputBorder}`, color: theme.inputText }}
                                    />
                                </div>
                            </div>
                            <div className="mt-3">
                                <SelectField icon={FileText} label="Case Status" name="status" options={statusOptions} />
                            </div>
                        </div>
                    </div>
                </form>

                {/* Footer Actions */}
                <div
                    className="px-5 py-3 flex items-center justify-end gap-3 flex-shrink-0"
                    style={{ borderTop: `1px solid ${theme.border}`, backgroundColor: theme.bg }}
                >
                    <button
                        type="button"
                        onClick={onClose}
                        className="px-4 py-2 text-sm font-medium rounded-md transition-colors"
                        style={{
                            color: theme.cancelText,
                            backgroundColor: theme.cancelBg,
                            border: `1px solid ${theme.cancelBorder}`
                        }}
                    >
                        Cancel
                    </button>
                    <button
                        type="submit"
                        onClick={handleSubmit}
                        className="px-4 py-2 text-sm font-medium text-white rounded-md transition-colors flex items-center gap-2"
                        style={{ backgroundColor: theme.accent }}
                        onMouseEnter={(e) => e.target.style.backgroundColor = '#0a5c66'}
                        onMouseLeave={(e) => e.target.style.backgroundColor = theme.accent}
                    >
                        <FileText className="w-4 h-4" />
                        Submit Case Report
                    </button>
                </div>
            </div>
        </div>
    );
};

export default AddCaseReportModal;