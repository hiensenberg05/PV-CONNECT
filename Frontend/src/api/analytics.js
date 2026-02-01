/**
 * Analytics API module
 * Connects to backend analytics endpoints
 */

const API_BASE = 'http://localhost:8000';

/**
 * Get vigigrade score statistics
 */
export const getStatistics = async () => {
    const response = await fetch(`${API_BASE}/api/v1/vigigrade/statistics`);
    if (!response.ok) {
        throw new Error(`Failed to fetch statistics: ${response.statusText}`);
    }
    return response.json();
};

/**
 * Get all cases from the database
 */
export const getCases = async () => {
    const response = await fetch(`${API_BASE}/api/cases`);
    if (!response.ok) {
        throw new Error(`Failed to fetch cases: ${response.statusText}`);
    }
    return response.json();
};

/**
 * Get FAERS signals from analytics
 */
export const getFaersSignals = async (limit = 100, minIc = 0) => {
    const response = await fetch(
        `${API_BASE}/api/v1/analytics/signals?limit=${limit}&min_ic=${minIc}`
    );
    if (!response.ok) {
        throw new Error(`Failed to fetch FAERS signals: ${response.statusText}`);
    }
    return response.json();
};

/**
 * Get FAERS statistics
 */
export const getFaersStats = async () => {
    const response = await fetch(`${API_BASE}/api/v1/analytics/stats`);
    if (!response.ok) {
        throw new Error(`Failed to fetch FAERS stats: ${response.statusText}`);
    }
    return response.json();
};

/**
 * Trigger batch score update
 */
export const batchUpdateScores = async (caseIds = null) => {
    const response = await fetch(`${API_BASE}/api/v1/vigigrade/batch-update`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ case_ids: caseIds })
    });
    if (!response.ok) {
        throw new Error(`Failed to batch update scores: ${response.statusText}`);
    }
    return response.json();
};
