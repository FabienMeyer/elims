// Wrapper file to provide an axios-like client from the auto-generated OpenAPI
import axios, { type AxiosInstance, type AxiosRequestConfig, type AxiosResponse } from 'axios';
import { OpenAPI } from './client/core/OpenAPI';

export * from './client';
export { ApiError } from './client/core/ApiError';

// Create an axios instance that respects OpenAPI configuration
const axiosInstance: AxiosInstance = axios.create();

// Create a client object that provides HTTP methods and configuration
export const client = {
  // HTTP Methods
  async GET<T = any>(url: string, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> {
    return axiosInstance.get<T>(url, { ...config });
  },
  async POST<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> {
    return axiosInstance.post<T>(url, data, { ...config });
  },
  async PUT<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> {
    return axiosInstance.put<T>(url, data, { ...config });
  },
  async DELETE<T = any>(url: string, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> {
    return axiosInstance.delete<T>(url, { ...config });
  },
  async PATCH<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> {
    return axiosInstance.patch<T>(url, data, { ...config });
  },

  // Configuration method to sync with OpenAPI
  setConfig(config: { baseUrl?: string; baseURL?: string }): void {
    const baseUrl = config.baseUrl || config.baseURL || '';
    axiosInstance.defaults.baseURL = baseUrl;
    OpenAPI.BASE = baseUrl;
  },

  // Direct axios instance access if needed
  axios: axiosInstance,
};
