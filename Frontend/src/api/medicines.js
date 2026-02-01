/**
 * Medicines API module
 * Connects to backend medicines endpoints
 */

const API_BASE = 'http://localhost:8000';

/**
 * Get medicines from the database
 * @param {Object} options - Query options
 * @param {number} options.limit - Maximum number of medicines (default 50)
 * @param {number} options.skip - Number to skip for pagination (default 0)
 * @param {string} options.search - Optional search query
 * @returns {Promise<{success: boolean, data: Array, total: number, limit: number, skip: number}>}
 */
export const getMedicines = async ({ limit = 50, skip = 0, search = '' } = {}) => {
    const params = new URLSearchParams({
        limit: limit.toString(),
        skip: skip.toString()
    });

    if (search) {
        params.append('search', search);
    }

    const response = await fetch(`${API_BASE}/api/v1/medicines?${params}`);

    if (!response.ok) {
        throw new Error(`Failed to fetch medicines: ${response.statusText}`);
    }

    return response.json();
};

/**
 * Get total count of medicines
 * @returns {Promise<{success: boolean, count: number}>}
 */
export const getMedicinesCount = async () => {
    const response = await fetch(`${API_BASE}/api/v1/medicines/count`);

    if (!response.ok) {
        throw new Error(`Failed to fetch medicines count: ${response.statusText}`);
    }

    return response.json();
};
