/**
 * API layer for ingredientes endpoints
 * Provides functions for communicating with backend API
 */
import axios from 'axios';
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
// Create Axios instance with JWT auth
const axiosInstance = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});
// Add JWT token to requests if available
axiosInstance.interceptors.request.use((config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});
/**
 * Fetch all active ingredients with optional pagination and filtering
 */
export async function fetchIngredientes(skip = 0, limit = 100, esAlergeno) {
    const params = { skip, limit };
    if (esAlergeno !== undefined) {
        params.es_alergeno = esAlergeno;
    }
    const response = await axiosInstance.get('/api/v1/ingredientes', { params });
    return response.data;
}
/**
 * Fetch a single ingredient by ID
 */
export async function fetchIngredienteById(id) {
    const response = await axiosInstance.get(`/api/v1/ingredientes/${id}`);
    return response.data;
}
/**
 * Create a new ingredient
 * Requires STOCK or ADMIN role
 */
export async function createIngrediente(data) {
    const response = await axiosInstance.post('/api/v1/ingredientes', data);
    return response.data;
}
/**
 * Update an existing ingredient
 * Requires STOCK or ADMIN role
 */
export async function updateIngrediente(id, data) {
    const response = await axiosInstance.put(`/api/v1/ingredientes/${id}`, data);
    return response.data;
}
/**
 * Delete (soft delete) an ingredient
 * Requires STOCK or ADMIN role
 */
export async function deleteIngrediente(id) {
    await axiosInstance.delete(`/api/v1/ingredientes/${id}`);
}
//# sourceMappingURL=api.js.map