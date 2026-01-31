import { useState, useEffect, useCallback } from 'react';
import { getStatistics, getCases, getFaersSignals, getFaersStats } from '../api/analytics';

/**
 * Custom hook for fetching analytics data from the backend
 * @returns {Object} - { statistics, cases, loading, error, refetch }
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
            // Trigger batch update first (optional, keep if needed)
            try {
                await import('../api/analytics').then(module => module.batchUpdateScores());
            } catch (e) {
                console.warn('Auto-analytics trigger failed:', e);
            }

            // Fetch all data in parallel
            const [statsResult, casesResult, faersSignalsResult, faersStatsResult] = await Promise.allSettled([
                getStatistics(),
                getCases(),
                getFaersSignals(),
                getFaersStats()
            ]);

            if (statsResult.status === 'fulfilled') setStatistics(statsResult.value);
            if (casesResult.status === 'fulfilled') setCases(casesResult.value || []);

            if (faersSignalsResult.status === 'fulfilled') {
                setFaersSignals(faersSignalsResult.value || []);
            } else {
                console.warn('Failed to fetch FAERS signals:', faersSignalsResult.reason);
            }

            if (faersStatsResult.status === 'fulfilled') {
                setFaersStats(faersStatsResult.value);
            } else {
                console.warn('Failed to fetch FAERS stats:', faersStatsResult.reason);
            }

        } catch (err) {
            console.error('Analytics fetch error:', err);
            setError(err.message || 'Failed to fetch analytics data');
        } finally {
            setLoading(false);
        }
    }, []);

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
        refetch: fetchData
    };
};

export default useAnalytics;
