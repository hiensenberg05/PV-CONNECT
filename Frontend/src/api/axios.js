import axios from 'axios';

// Create axios instance with base configuration
const axiosInstance = axios.create({
    baseURL: 'http://localhost:8000',
    headers: {
        'Content-Type': 'application/json',
    },
});

// Request interceptor to add JWT token to headers
axiosInstance.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Response interceptor for error handling
axiosInstance.interceptors.response.use(
    (response) => {
        return response;
    },
    (error) => {
        // Only redirect to login for 401 on PROTECTED routes (not on login itself)
        const isLoginRequest = error.config?.url?.includes('/auth/login');

        if (error.response?.status === 401 && !isLoginRequest) {
            // Token expired or invalid, clear storage and redirect to login
            localStorage.removeItem('access_token');
            localStorage.removeItem('user');
            window.location.href = '/';
        }
        return Promise.reject(error);
    }
);

export default axiosInstance;
