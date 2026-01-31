import axiosInstance from './axios';

/**
 * Login employee with employee ID and password
 * @param {string} employeeId - Employee ID (e.g., EMP001)
 * @param {string} password - Employee password
 * @returns {Promise} - Promise with token data
 */
export const login = async (employeeId, password) => {
    // OAuth2PasswordRequestForm expects form data, not JSON
    const formData = new URLSearchParams();
    formData.append('username', employeeId); // OAuth2 uses 'username' field
    formData.append('password', password);

    const response = await axiosInstance.post('/auth/login', formData, {
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
    });

    // Store token in localStorage
    if (response.data.access_token) {
        localStorage.setItem('access_token', response.data.access_token);
    }

    return response.data;
};

/**
 * Logout user (clear local storage)
 */
export const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
};

/**
 * Check if user is authenticated
 * @returns {boolean} - True if user has a token
 */
export const isAuthenticated = () => {
    return !!localStorage.getItem('access_token');
};

/**
 * Get stored token
 * @returns {string|null} - Access token or null
 */
export const getToken = () => {
    return localStorage.getItem('access_token');
};
