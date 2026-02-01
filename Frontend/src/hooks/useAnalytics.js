import { useState, useEffect, useCallback } from 'react';
import { getStatistics, getCases, getFaersSignals, getFaersStats, batchUpdateScores } from '../api/analytics';

/**
 * Custom hook for analytics data - fetches from backend API
 * @returns {Object} - { statistics, cases, faersSignals, faersStats, loading, error, refetch, updateScores }
 */
const useAnalytics = () => {
    const [statistics, setStatistics] = useState(null);
    const [cases, setCases] = useState([]);
    const [faersSignals, setFaersSignals] = useState([]);
    const [faersStats, setFaersStats] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const fetchData = useCallback(async () => {
        setLoading(true);
        setError(null);

        try {
            // Fetch all data in parallel
            const results = await Promise.allSettled([
                getStatistics(),
                getCases(),
                getFaersSignals(),
                getFaersStats()
            ]);

            // Handle statistics
            if (results[0].status === 'fulfilled') {
                setStatistics(results[0].value);
            } else {
                console.warn('Failed to fetch statistics:', results[0].reason);
            }

            // Handle cases
            if (results[1].status === 'fulfilled') {
                setCases(results[1].value || []);
            } else {
                console.warn('Failed to fetch cases:', results[1].reason);
            }

            // Handle FAERS signals
            if (results[2].status === 'fulfilled') {
                setFaersSignals(results[2].value || []);
            } else {
                console.warn('Failed to fetch FAERS signals:', results[2].reason);
            }

            // Handle FAERS stats
            if (results[3].status === 'fulfilled') {
                setFaersStats(results[3].value);
            } else {
                console.warn('Failed to fetch FAERS stats:', results[3].reason);
            }

            // Check if all requests failed
            const allFailed = results.every(r => r.status === 'rejected');
            if (allFailed) {
                setError('Failed to fetch analytics data. Please check your connection.');
            }

        } catch (err) {
            console.error('Analytics fetch error:', err);
            setError(err.message || 'Failed to fetch analytics data');
        } finally {
            setLoading(false);
        }
    }, []);

    const updateScores = useCallback(async (caseIds = null) => {
        try {
            const result = await batchUpdateScores(caseIds);
            // Refetch data after update
            await fetchData();
            return result;
        } catch (err) {
            console.error('Score update error:', err);
            throw err;
        }
    }, [fetchData]);

    useEffect(() => {
        fetchData();
    }, [fetchData]);

    return {
        statistics,
        cases,
        faersSignals,
        faersStats,
        loading,
        error,
        refetch: fetchData,
        updateScores
    };
};

export default useAnalytics;
