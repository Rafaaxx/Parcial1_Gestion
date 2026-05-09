/**
 * Environment variables with type safety
 */
export const env = {
    API_BASE_URL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1',
    DEBUG: import.meta.env.VITE_DEBUG === 'true',
    APP_NAME: import.meta.env.VITE_APP_NAME || 'Food Store',
};
//# sourceMappingURL=env.js.map