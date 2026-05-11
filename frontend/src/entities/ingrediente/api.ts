/**
 * API layer for ingredientes endpoints
 * Provides functions for communicating with backend API
 */

import axios from 'axios';
import type {
  IngredienteRead,
  IngredienteCreate,
  IngredienteUpdate,
  IngredienteListResponse,
} from './types';

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
export async function fetchIngredientes(
  skip: number = 0,
  limit: number = 100,
  esAlergeno?: boolean
): Promise<IngredienteListResponse> {
  const params: Record<string, any> = { skip, limit };
  if (esAlergeno !== undefined) {
    params.es_alergeno = esAlergeno;
  }

  const response = await axiosInstance.get<IngredienteListResponse>('/api/v1/ingredientes', {
    params,
  });
  return response.data;
}

/**
 * Fetch a single ingredient by ID
 */
export async function fetchIngredienteById(id: number): Promise<IngredienteRead> {
  const response = await axiosInstance.get<IngredienteRead>(`/api/v1/ingredientes/${id}`);
  return response.data;
}

/**
 * Create a new ingredient
 * Requires STOCK or ADMIN role
 */
export async function createIngrediente(data: IngredienteCreate): Promise<IngredienteRead> {
  const response = await axiosInstance.post<IngredienteRead>('/api/v1/ingredientes', data);
  return response.data;
}

/**
 * Update an existing ingredient
 * Requires STOCK or ADMIN role
 */
export async function updateIngrediente(
  id: number,
  data: IngredienteUpdate
): Promise<IngredienteRead> {
  const response = await axiosInstance.put<IngredienteRead>(`/api/v1/ingredientes/${id}`, data);
  return response.data;
}

/**
 * Delete (soft delete) an ingredient
 * Requires STOCK or ADMIN role
 */
export async function deleteIngrediente(id: number): Promise<void> {
  await axiosInstance.delete(`/api/v1/ingredientes/${id}`);
}
