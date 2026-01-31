import axiosInstance from './axios';

/**
 * Get aggregate statistics from VigiGrade analytics
 * @returns {Promise} - Promise with statistics data
 */
export const getStatistics = async () => {
    const response = await axiosInstance.get('/api/v1/vigigrade/statistics');
    return response.data;
};

/**
 * Get all cases from the database
 * @returns {Promise} - Promise with array of cases
 */
export const getCases = async () => {
    const response = await axiosInstance.get('/api/cases');
    return response.data;
};

/**
 * Get confidence score for a specific case
 * @param {string} caseId - Case identifier
 * @returns {Promise} - Promise with score data
 */
export const getCaseScore = async (caseId) => {
    const response = await axiosInstance.get(`/api/v1/vigigrade/cases/${caseId}/score`);
    return response.data;
};

/**
 * Trigger batch update of all case scores
 * @param {string[]} caseIds - Optional list of specific case IDs
 * @returns {Promise} - Promise with update result
 */
export const batchUpdateScores = async (caseIds = null) => {
    const response = await axiosInstance.post('/api/v1/vigigrade/batch-update', {
        case_ids: caseIds
    });
    return response.data;
};

export const getFaersSignals = async (limit = 100) => {
    const response = await axiosInstance.get(`/api/v1/analytics/signals?limit=${limit}`);
    return response.data;
};

export const getFaersStats = async () => {
    const response = await axiosInstance.get('/api/v1/analytics/stats');
    return response.data;
};
