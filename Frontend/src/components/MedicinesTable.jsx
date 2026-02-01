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

    // Fetch medicines from API
    const fetchMedicines = async () => {
        setLoading(true);
        setError(null);
        try {
            const skip = (currentPage - 1) * itemsPerPage;
            const response = await getMedicines({
                limit: itemsPerPage,
                skip,
                search: searchQuery
            });

            if (response.success) {
                setMedicines(response.data || []);
                setTotal(response.total || 0);
            } else {
                setError(response.error || 'Failed to fetch medicines');
            }
        } catch (err) {
            console.error('Error fetching medicines:', err);
            setError(err.message || 'Failed to fetch medicines');
        } finally {
            setLoading(false);
        }
    };

    // Fetch on mount and when search/page changes
    useEffect(() => {
        fetchMedicines();
    }, [currentPage, searchQuery]);

    // Debounce search
    useEffect(() => {
        const timer = setTimeout(() => {
            setCurrentPage(1); // Reset to first page on search
        }, 300);
        return () => clearTimeout(timer);
    }, [searchQuery]);

    const totalPages = Math.ceil(total / itemsPerPage);

    // Pagination handlers
    const handlePrevPage = () => {
        if (currentPage > 1) {
            setCurrentPage(prev => prev - 1);
        }
    };

    const handleNextPage = () => {
        if (currentPage < totalPages) {
            setCurrentPage(prev => prev + 1);
        }
    };

    if (error) {
        return (
            <div className="rounded-lg p-6 text-center" style={{ backgroundColor: theme.bg, border: `1px solid ${theme.border}` }}>
                <AlertCircle className="w-10 h-10 mx-auto mb-3" style={{ color: '#ef4444' }} />
                <p className="text-sm" style={{ color: theme.textSecondary }}>{error}</p>
                <button
                    onClick={fetchMedicines}
                    className="mt-3 px-4 py-2 rounded-md text-sm font-medium text-white"
                    style={{ backgroundColor: theme.accent }}
                >
                    Retry
                </button>
            </div>
        );
    }

    return (
        <div className="rounded-lg overflow-hidden" style={{ backgroundColor: theme.bg, border: `1px solid ${theme.border}` }}>
            {/* Header with Search */}
            <div className="px-5 py-4 flex items-center justify-between" style={{ borderBottom: `1px solid ${theme.border}` }}>
                <div className="flex items-center gap-2">
                    <Pill className="w-5 h-5" style={{ color: theme.accent }} />
                    <h2 className="text-lg font-semibold" style={{ color: theme.text }}>Medicines Database</h2>
                    <span className="px-2 py-0.5 text-xs font-medium rounded-full" style={{ backgroundColor: theme.accentLight, color: theme.accent }}>
                        {total} medicines
                    </span>
                </div>

                <div className="relative">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4" style={{ color: theme.textSecondary }} />
                    <input
                        type="text"
                        placeholder="Search medicines..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="pl-9 pr-4 py-2 text-sm rounded-md outline-none w-64"
                        style={{
                            backgroundColor: theme.inputBg,
                            border: `1px solid ${theme.inputBorder}`,
                            color: theme.text
                        }}
                    />
                </div>
            </div>

            {/* Table */}
            {loading ? (
                <div className="flex items-center justify-center py-16">
                    <Loader2 className="w-8 h-8 animate-spin" style={{ color: theme.accent }} />
                </div>
            ) : (
                <>
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
                                    Known Side Effects
                                </th>
                                <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wider" style={{ color: theme.textSecondary }}>
                                    Actions
                                </th>
                            </tr>
                        </thead>
                        <tbody>
                            {medicines.length === 0 ? (
                                <tr>
                                    <td colSpan="4" className="px-5 py-12 text-center" style={{ color: theme.textSecondary }}>
                                        No medicines found
                                    </td>
                                </tr>
                            ) : (
                                medicines.map((medicine) => (
                                    <React.Fragment key={medicine.id}>
                                        <tr
                                            className="cursor-pointer"
                                            style={{ borderBottom: `1px solid ${theme.border}` }}
                                            onClick={() => setExpandedRow(expandedRow === medicine.id ? null : medicine.id)}
                                            onMouseEnter={(e) => e.currentTarget.style.backgroundColor = theme.hoverBg}
                                            onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
                                        >
                                            <td className="px-5 py-4">
                                                <div className="flex items-center gap-2">
                                                    <Pill className="w-4 h-4" style={{ color: theme.accent }} />
                                                    <span className="font-medium" style={{ color: theme.text }}>{medicine.drug_name}</span>
                                                </div>
                                            </td>
                                            <td className="px-5 py-4">
                                                <span className="text-sm" style={{ color: theme.textSecondary }}>{medicine.generic_name}</span>
                                            </td>
                                            <td className="px-5 py-4">
                                                <div className="flex flex-wrap gap-1">
                                                    {(medicine.known_side_effects || []).slice(0, 3).map((effect, idx) => (
                                                        <span
                                                            key={idx}
                                                            className="px-2 py-0.5 text-xs rounded-full"
                                                            style={{ backgroundColor: theme.bgSecondary, color: theme.textSecondary }}
                                                        >
                                                            {effect}
                                                        </span>
                                                    ))}
                                                    {(medicine.known_side_effects || []).length > 3 && (
                                                        <span className="text-xs" style={{ color: theme.textSecondary }}>
                                                            +{medicine.known_side_effects.length - 3} more
                                                        </span>
                                                    )}
                                                </div>
                                            </td>
                                            <td className="px-5 py-4">
                                                <button
                                                    className="px-3 py-1 text-xs font-medium rounded-md"
                                                    style={{ backgroundColor: theme.accentLight, color: theme.accent }}
                                                >
                                                    <FileText className="w-3 h-3 inline mr-1" />
                                                    Details
                                                </button>
                                            </td>
                                        </tr>

                                        {/* Expanded Row */}
                                        {expandedRow === medicine.id && (
                                            <tr style={{ backgroundColor: theme.bgSecondary }}>
                                                <td colSpan="4" className="px-5 py-4">
                                                    <div className="grid grid-cols-3 gap-6">
                                                        <div>
                                                            <h4 className="text-xs font-semibold uppercase mb-2" style={{ color: theme.textSecondary }}>
                                                                Common Dosages
                                                            </h4>
                                                            <div className="flex flex-wrap gap-1">
                                                                {(medicine.common_dosages || []).map((dosage, idx) => (
                                                                    <span
                                                                        key={idx}
                                                                        className="px-2 py-1 text-xs rounded"
                                                                        style={{ backgroundColor: theme.bg, color: theme.text }}
                                                                    >
                                                                        {dosage}
                                                                    </span>
                                                                ))}
                                                            </div>
                                                        </div>
                                                        <div>
                                                            <h4 className="text-xs font-semibold uppercase mb-2" style={{ color: theme.textSecondary }}>
                                                                <Globe className="w-3 h-3 inline mr-1" />
                                                                Approved Countries
                                                            </h4>
                                                            <div className="flex flex-wrap gap-1">
                                                                {(medicine.approved_countries || []).map((country, idx) => (
                                                                    <span
                                                                        key={idx}
                                                                        className="px-2 py-1 text-xs rounded"
                                                                        style={{ backgroundColor: theme.bg, color: theme.text }}
                                                                    >
                                                                        {country}
                                                                    </span>
                                                                ))}
                                                            </div>
                                                        </div>
                                                        <div>
                                                            <h4 className="text-xs font-semibold uppercase mb-2" style={{ color: theme.textSecondary }}>
                                                                <AlertCircle className="w-3 h-3 inline mr-1" />
                                                                All Side Effects
                                                            </h4>
                                                            <div className="flex flex-wrap gap-1">
                                                                {(medicine.known_side_effects || []).map((effect, idx) => (
                                                                    <span
                                                                        key={idx}
                                                                        className="px-2 py-1 text-xs rounded"
                                                                        style={{ backgroundColor: '#fef3c7', color: '#92400e' }}
                                                                    >
                                                                        {effect}
                                                                    </span>
                                                                ))}
                                                            </div>
                                                        </div>
                                                    </div>
                                                </td>
                                            </tr>
                                        )}
                                    </React.Fragment>
                                ))
                            )}
                        </tbody>
                    </table>

                    {/* Pagination */}
                    <div className="px-5 py-4 flex items-center justify-between" style={{ borderTop: `1px solid ${theme.border}` }}>
                        <span className="text-sm" style={{ color: theme.textSecondary }}>
                            Showing {medicines.length > 0 ? (currentPage - 1) * itemsPerPage + 1 : 0} to {Math.min(currentPage * itemsPerPage, total)} of {total} medicines
                        </span>
                        <div className="flex items-center gap-2">
                            <button
                                onClick={handlePrevPage}
                                disabled={currentPage === 1}
                                className="p-2 rounded-md disabled:opacity-50 disabled:cursor-not-allowed"
                                style={{ backgroundColor: theme.bgSecondary, color: theme.text }}
                            >
                                <ChevronLeft className="w-4 h-4" />
                            </button>
                            <span className="text-sm font-medium" style={{ color: theme.text }}>
                                Page {currentPage} of {totalPages || 1}
                            </span>
                            <button
                                onClick={handleNextPage}
                                disabled={currentPage >= totalPages}
                                className="p-2 rounded-md disabled:opacity-50 disabled:cursor-not-allowed"
                                style={{ backgroundColor: theme.bgSecondary, color: theme.text }}
                            >
                                <ChevronRight className="w-4 h-4" />
                            </button>
                        </div>
                    </div>
                </>
            )}
        </div>
    );
};

export default MedicinesTable;
