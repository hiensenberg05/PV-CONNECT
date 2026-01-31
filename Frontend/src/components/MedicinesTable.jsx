// Frontend/src/components/MedicinesTable.jsx
/**
 * Medicines Database Table Component
 * Displays medicines from the drugs_database collection
 */

import React, { useState, useEffect } from 'react';
import { Search, Pill, AlertCircle, ChevronLeft, ChevronRight, Globe, FileText, Loader2 } from 'lucide-react';
import { getMedicines } from '../api/medicines';
import useThemeStore from '../store/themeStore';

const MedicinesTable = () => {
    const { darkMode } = useThemeStore();
    const [medicines, setMedicines] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [searchQuery, setSearchQuery] = useState('');
    const [currentPage, setCurrentPage] = useState(1);
    const [total, setTotal] = useState(0);
    const [expandedRow, setExpandedRow] = useState(null);

    const itemsPerPage = 10;

    // Theme colors matching dashboard
    const theme = {
        bg: darkMode ? '#111827' : '#ffffff',
        bgSecondary: darkMode ? '#1f2937' : '#f9fafb',
        text: darkMode ? '#f9fafb' : '#111827',
        textSecondary: darkMode ? '#9ca3af' : '#6b7280',
        border: darkMode ? '#374151' : '#e5e7eb',
        inputBg: darkMode ? '#1f2937' : '#ffffff',
        inputBorder: darkMode ? '#4b5563' : '#d1d5db',
        hoverBg: darkMode ? '#374151' : '#f3f4f6',
        accent: '#073d44',
        accentLight: darkMode ? '#0a5c66' : '#e0f7fa',
    };

    // Fetch medicines
    useEffect(() => {
        const fetchMedicines = async () => {
            setLoading(true);
            const skip = (currentPage - 1) * itemsPerPage;
            const result = await getMedicines(itemsPerPage, skip, searchQuery);

            if (result.success) {
                setMedicines(result.data);
                setTotal(result.total);
                setError(null);
            } else {
                setError(result.error || 'Failed to fetch medicines');
                setMedicines([]);
            }
            setLoading(false);
        };

        const debounceTimer = setTimeout(fetchMedicines, 300);
        return () => clearTimeout(debounceTimer);
    }, [currentPage, searchQuery]);

    const totalPages = Math.ceil(total / itemsPerPage);

    // Severity color for side effects
    const getSideEffectColor = (effect) => {
        const lowerEffect = effect.toLowerCase();
        if (lowerEffect.includes('severe') || lowerEffect.includes('death') || lowerEffect.includes('fatal')) {
            return { bg: darkMode ? '#7f1d1d' : '#fef2f2', text: darkMode ? '#fca5a5' : '#dc2626' };
        }
        if (lowerEffect.includes('moderate') || lowerEffect.includes('pain') || lowerEffect.includes('bleeding')) {
            return { bg: darkMode ? '#78350f' : '#fffbeb', text: darkMode ? '#fcd34d' : '#d97706' };
        }
        return { bg: darkMode ? '#064e3b' : '#ecfdf5', text: darkMode ? '#6ee7b7' : '#059669' };
    };

    return (
        <div className="rounded-xl overflow-hidden" style={{ backgroundColor: theme.bg, border: `1px solid ${theme.border}` }}>
            {/* Header */}
            <div className="px-5 py-4 flex items-center justify-between" style={{ borderBottom: `1px solid ${theme.border}` }}>
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-lg flex items-center justify-center" style={{ backgroundColor: theme.accent }}>
                        <Pill className="w-5 h-5 text-white" />
                    </div>
                    <div>
                        <h2 className="text-lg font-semibold" style={{ color: theme.text }}>Medicines Database</h2>
                        <p className="text-sm" style={{ color: theme.textSecondary }}>
                            {total.toLocaleString()} medicines available
                        </p>
                    </div>
                </div>

                {/* Search */}
                <div className="relative w-72">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4" style={{ color: theme.textSecondary }} />
                    <input
                        type="text"
                        placeholder="Search medicines..."
                        value={searchQuery}
                        onChange={(e) => { setSearchQuery(e.target.value); setCurrentPage(1); }}
                        className="w-full pl-10 pr-4 py-2 text-sm rounded-lg outline-none transition-all"
                        style={{
                            backgroundColor: theme.inputBg,
                            border: `1px solid ${theme.inputBorder}`,
                            color: theme.text
                        }}
                    />
                </div>
            </div>

            {/* Table */}
            <div className="overflow-x-auto">
                {loading ? (
                    <div className="flex items-center justify-center py-16">
                        <Loader2 className="w-8 h-8 animate-spin" style={{ color: theme.accent }} />
                        <span className="ml-3 text-sm" style={{ color: theme.textSecondary }}>Loading medicines...</span>
                    </div>
                ) : error ? (
                    <div className="flex items-center justify-center py-16 text-red-500">
                        <AlertCircle className="w-5 h-5 mr-2" />
                        <span>{error}</span>
                    </div>
                ) : medicines.length === 0 ? (
                    <div className="flex flex-col items-center justify-center py-16">
                        <Pill className="w-12 h-12 mb-3" style={{ color: theme.textSecondary }} />
                        <p className="text-sm" style={{ color: theme.textSecondary }}>No medicines found</p>
                    </div>
                ) : (
                    <table className="w-full">
                        <thead>
                            <tr style={{ backgroundColor: theme.bgSecondary }}>
                                <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wider" style={{ color: theme.textSecondary }}>
                                    Drug Name
                                </th>
                                <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wider" style={{ color: theme.textSecondary }}>
                                    Generic Name
                                </th>
                                <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wider" style={{ color: theme.textSecondary }}>
                                    Side Effects
                                </th>
                                <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wider" style={{ color: theme.textSecondary }}>
                                    Dosages
                                </th>
                                <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wider" style={{ color: theme.textSecondary }}>
                                    Countries
                                </th>
                            </tr>
                        </thead>
                        <tbody>
                            {medicines.map((medicine, index) => (
                                <React.Fragment key={medicine.id}>
                                    <tr
                                        className="cursor-pointer transition-colors"
                                        style={{
                                            borderBottom: `1px solid ${theme.border}`,
                                            backgroundColor: expandedRow === medicine.id ? theme.hoverBg : 'transparent'
                                        }}
                                        onClick={() => setExpandedRow(expandedRow === medicine.id ? null : medicine.id)}
                                        onMouseEnter={(e) => expandedRow !== medicine.id && (e.currentTarget.style.backgroundColor = theme.hoverBg)}
                                        onMouseLeave={(e) => expandedRow !== medicine.id && (e.currentTarget.style.backgroundColor = 'transparent')}
                                    >
                                        <td className="px-5 py-4">
                                            <div className="flex items-center gap-3">
                                                <div className="w-8 h-8 rounded-lg flex items-center justify-center"
                                                    style={{ backgroundColor: theme.accentLight }}>
                                                    <Pill className="w-4 h-4" style={{ color: theme.accent }} />
                                                </div>
                                                <span className="font-medium text-sm" style={{ color: theme.text }}>
                                                    {medicine.drug_name}
                                                </span>
                                            </div>
                                        </td>
                                        <td className="px-5 py-4">
                                            <span className="text-sm capitalize" style={{ color: theme.textSecondary }}>
                                                {medicine.generic_name}
                                            </span>
                                        </td>
                                        <td className="px-5 py-4">
                                            <div className="flex flex-wrap gap-1">
                                                {medicine.known_side_effects?.slice(0, 2).map((effect, i) => {
                                                    const colors = getSideEffectColor(effect);
                                                    return (
                                                        <span
                                                            key={i}
                                                            className="px-2 py-0.5 rounded-full text-xs font-medium"
                                                            style={{ backgroundColor: colors.bg, color: colors.text }}
                                                        >
                                                            {effect}
                                                        </span>
                                                    );
                                                })}
                                                {medicine.known_side_effects?.length > 2 && (
                                                    <span className="px-2 py-0.5 rounded-full text-xs" style={{ backgroundColor: theme.bgSecondary, color: theme.textSecondary }}>
                                                        +{medicine.known_side_effects.length - 2}
                                                    </span>
                                                )}
                                            </div>
                                        </td>
                                        <td className="px-5 py-4">
                                            <span className="text-sm" style={{ color: theme.textSecondary }}>
                                                {medicine.common_dosages?.length || 0} forms
                                            </span>
                                        </td>
                                        <td className="px-5 py-4">
                                            <div className="flex items-center gap-1">
                                                <Globe className="w-3.5 h-3.5" style={{ color: theme.textSecondary }} />
                                                <span className="text-sm" style={{ color: theme.textSecondary }}>
                                                    {medicine.approved_countries?.length || 0}
                                                </span>
                                            </div>
                                        </td>
                                    </tr>

                                    {/* Expanded Row */}
                                    {expandedRow === medicine.id && (
                                        <tr style={{ backgroundColor: theme.bgSecondary }}>
                                            <td colSpan={5} className="px-5 py-4">
                                                <div className="grid grid-cols-3 gap-6">
                                                    {/* Side Effects */}
                                                    <div>
                                                        <h4 className="text-xs font-semibold uppercase mb-2 flex items-center gap-1" style={{ color: theme.textSecondary }}>
                                                            <AlertCircle className="w-3.5 h-3.5" /> Known Side Effects
                                                        </h4>
                                                        <div className="flex flex-wrap gap-1">
                                                            {medicine.known_side_effects?.map((effect, i) => {
                                                                const colors = getSideEffectColor(effect);
                                                                return (
                                                                    <span key={i} className="px-2 py-1 rounded text-xs" style={{ backgroundColor: colors.bg, color: colors.text }}>
                                                                        {effect}
                                                                    </span>
                                                                );
                                                            })}
                                                            {(!medicine.known_side_effects || medicine.known_side_effects.length === 0) && (
                                                                <span className="text-xs" style={{ color: theme.textSecondary }}>No data</span>
                                                            )}
                                                        </div>
                                                    </div>

                                                    {/* Dosages */}
                                                    <div>
                                                        <h4 className="text-xs font-semibold uppercase mb-2 flex items-center gap-1" style={{ color: theme.textSecondary }}>
                                                            <FileText className="w-3.5 h-3.5" /> Common Dosages
                                                        </h4>
                                                        <div className="flex flex-wrap gap-1">
                                                            {medicine.common_dosages?.map((dosage, i) => (
                                                                <span key={i} className="px-2 py-1 rounded text-xs" style={{ backgroundColor: theme.bg, color: theme.text, border: `1px solid ${theme.border}` }}>
                                                                    {dosage}
                                                                </span>
                                                            ))}
                                                            {(!medicine.common_dosages || medicine.common_dosages.length === 0) && (
                                                                <span className="text-xs" style={{ color: theme.textSecondary }}>No data</span>
                                                            )}
                                                        </div>
                                                    </div>

                                                    {/* Countries */}
                                                    <div>
                                                        <h4 className="text-xs font-semibold uppercase mb-2 flex items-center gap-1" style={{ color: theme.textSecondary }}>
                                                            <Globe className="w-3.5 h-3.5" /> Approved Countries
                                                        </h4>
                                                        <div className="flex flex-wrap gap-1">
                                                            {medicine.approved_countries?.map((country, i) => (
                                                                <span key={i} className="px-2 py-1 rounded text-xs" style={{ backgroundColor: theme.accentLight, color: theme.accent }}>
                                                                    {country}
                                                                </span>
                                                            ))}
                                                            {(!medicine.approved_countries || medicine.approved_countries.length === 0) && (
                                                                <span className="text-xs" style={{ color: theme.textSecondary }}>No data</span>
                                                            )}
                                                        </div>
                                                    </div>
                                                </div>
                                            </td>
                                        </tr>
                                    )}
                                </React.Fragment>
                            ))}
                        </tbody>
                    </table>
                )}
            </div>

            {/* Pagination */}
            {!loading && medicines.length > 0 && (
                <div className="px-5 py-3 flex items-center justify-between" style={{ borderTop: `1px solid ${theme.border}` }}>
                    <span className="text-sm" style={{ color: theme.textSecondary }}>
                        Showing {((currentPage - 1) * itemsPerPage) + 1} to {Math.min(currentPage * itemsPerPage, total)} of {total}
                    </span>
                    <div className="flex items-center gap-2">
                        <button
                            onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                            disabled={currentPage === 1}
                            className="p-2 rounded-lg transition-colors disabled:opacity-50"
                            style={{ backgroundColor: theme.bgSecondary, color: theme.text }}
                        >
                            <ChevronLeft className="w-4 h-4" />
                        </button>
                        <span className="px-3 py-1 text-sm rounded" style={{ backgroundColor: theme.accent, color: 'white' }}>
                            {currentPage}
                        </span>
                        <span className="text-sm" style={{ color: theme.textSecondary }}>of {totalPages}</span>
                        <button
                            onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                            disabled={currentPage === totalPages}
                            className="p-2 rounded-lg transition-colors disabled:opacity-50"
                            style={{ backgroundColor: theme.bgSecondary, color: theme.text }}
                        >
                            <ChevronRight className="w-4 h-4" />
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
};

export default MedicinesTable;
