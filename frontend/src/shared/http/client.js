/**
 * Axios HTTP client with base configuration
 */
import axios from 'axios';
import { env } from '@/config/env';
export const apiClient = axios.create({
    baseURL: env.API_BASE_URL,
    timeout: 30000,
    headers: {
        'Content-Type': 'application/json',
    },
});
/**
 * Log request details in debug mode
 */
apiClient.interceptors.request.use((config) => {
    if (env.DEBUG) {
        console.log(`[API] ${config.method?.toUpperCase()} ${config.url}`);
    }
    return config;
});
/**
 * Log response and handle errors
 */
apiClient.interceptors.response.use((response) => {
    if (env.DEBUG) {
        console.log(`[API] ${response.status} ${response.config.method?.toUpperCase()} ${response.config.url}`);
    }
    return response;
}, (error) => {
    if (env.DEBUG && error.response) {
        console.error(`[API] Error ${error.response.status}`, error.response.data);
    }
    return Promise.reject(error);
});
export default apiClient;
//# sourceMappingURL=client.js.map