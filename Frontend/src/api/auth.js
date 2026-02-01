/**
 * Authentication API module
 * Connects to backend auth endpoints
 */

const API_BASE = 'http://localhost:8000';

/**
 * Login with employee credentials
 * @param {string} employeeId - Employee ID (e.g., EMP001)
 * @param {string} password - Password
 * @returns {Promise<{access_token: string, token_type: string}>}
 */
export const login = async (employeeId, password) => {
    const formData = new URLSearchParams();
    formData.append('username', employeeId);
    formData.append('password', password);

    const response = await fetch(`${API_BASE}/auth/login`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: formData
    });

    if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        const err = new Error(error.detail || 'Login failed');
        err.response = { status: response.status, data: error };
        throw err;
    }

    const data = await response.json();

    // Store token in localStorage
    localStorage.setItem('access_token', data.access_token);

    return data;
};

/**
 * Logout - clear stored token
 */
export const logout = () => {
    localStorage.removeItem('access_token');
};

/**
 * Get stored access token
 */
export const getToken = () => {
    return localStorage.getItem('access_token');
};

/**
 * Check if user is authenticated
 */
export const isAuthenticated = () => {
    return !!getToken();
};
