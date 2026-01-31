// Frontend/src/api/medicines.js
/**
 * API functions for medicines database
 */

const API_BASE_URL = 'http://localhost:8000';

/**
 * Fetch medicines from the database
 * @param {number} limit - Max medicines to fetch
 * @param {number} skip - Number to skip for pagination
 * @param {string} search - Optional search query
 */
export const getMedicines = async (limit = 50, skip = 0, search = '') => {
    try {
        let url = `${API_BASE_URL}/api/v1/medicines?limit=${limit}&skip=${skip}`;
        if (search) {
            url += `&search=${encodeURIComponent(search)}`;
        }

        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error fetching medicines:', error);
        return { success: false, data: [], total: 0, error: error.message };
    }
};

/**
 * Get total count of medicines
 */
export const getMedicinesCount = async () => {
    try {
        const response = await fetch(`${API_BASE_URL}/api/v1/medicines/count`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error('Error fetching medicines count:', error);
        return { success: false, count: 0, error: error.message };
    }
};
