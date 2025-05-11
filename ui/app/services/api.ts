// API service for communication with the backend

import axios from 'axios';
import type { InternalAxiosRequestConfig } from 'axios';
import type { AuthTokens, LoginCredentials, RegisterData, User } from '../types/auth';
import type { Device, DeviceCreate, DeviceResponse } from '../types/device';

// Define base URL - adjust this based on your deployment setup
const API_BASE_URL = 'http://localhost:8000';

// Create axios instance with base configuration
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to all requests if available
apiClient.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = localStorage.getItem('token');
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Types based on backend models
export interface SensorData {
  device_id: string;
  sensor_type: string;
  value: number;
  unit: string;
  timestamp: string;
  location: string;
  metadata?: string;
}

export interface SensorDataResponse {
  data: SensorData[];
  total_count: number;
}

export interface SensorStats {
  device_id: string;
  sensor_type: string;
  min_value: number;
  max_value: number;
  avg_value: number;
  unit: string;
  from_timestamp: string;
  to_timestamp: string;
}

export interface SensorStatsResponse {
  data: SensorStats[];
}

// Authentication API methods
export const authApi = {
  // Register a new user
  register: async (userData: RegisterData): Promise<User> => {
    const response = await apiClient.post<User>('/auth/register', userData);
    return response.data;
  },

  // Login and get access token
  login: async (credentials: LoginCredentials): Promise<AuthTokens> => {
    // For login, we need to use form data format as required by OAuth2
    const formData = new FormData();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);
    
    const response = await apiClient.post<AuthTokens>(
      '/auth/token',
      formData,
      {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      }
    );
    
    // Save token to localStorage for subsequent requests
    if (response.data.access_token) {
      localStorage.setItem('token', response.data.access_token);
    }
    
    return response.data;
  },

  // Get current authenticated user
  getCurrentUser: async (): Promise<User> => {
    const response = await apiClient.get<User>('/auth/me');
    return response.data;
  },

  // Logout - just remove token from storage
  logout: (): void => {
    localStorage.removeItem('token');
  },
};

// Devices API methods
export const deviceApi = {
  // Get all devices
  getAllDevices: async (): Promise<DeviceResponse> => {
    const response = await apiClient.get<DeviceResponse>('/devices');
    return response.data;
  },

  // Get a single device by ID
  getDevice: async (deviceId: string): Promise<Device> => {
    const response = await apiClient.get<Device>(`/devices/${deviceId}`);
    return response.data;
  },

  // Create a new device (admin only)
  createDevice: async (deviceData: DeviceCreate): Promise<Device> => {
    const response = await apiClient.post<Device>('/devices', deviceData);
    return response.data;
  },

  // Update a device (admin only)
  updateDevice: async (deviceId: string, deviceData: Partial<DeviceCreate>): Promise<Device> => {
    const response = await apiClient.put<Device>(`/devices/${deviceId}`, deviceData);
    return response.data;
  },

  // Delete a device (admin only)
  deleteDevice: async (deviceId: string): Promise<void> => {
    await apiClient.delete(`/devices/${deviceId}`);
  },
};

// API client functions
export const api = {
  // Get latest sensor data
  getLatestSensorData: async (
    params: {
      device_id?: string;
      sensor_type?: string;
      location?: string;
      limit?: number;
    } = {}
  ): Promise<SensorDataResponse> => {
    const response = await apiClient.get<SensorDataResponse>('/sensor-data/latest', { params });
    return response.data;
  },

  // Get historical sensor data
  getHistoricalSensorData: async (
    params: {
      from_timestamp: string;
      to_timestamp: string;
      device_id?: string;
      sensor_type?: string;
      location?: string;
      limit?: number;
    }
  ): Promise<SensorDataResponse> => {
    const response = await apiClient.get<SensorDataResponse>('/sensor-data/historical', { params });
    return response.data;
  },

  // Get sensor statistics
  getSensorStats: async (
    params: {
      from_timestamp: string;
      to_timestamp: string;
      device_id?: string;
      sensor_type?: string;
      location?: string;
    }
  ): Promise<SensorStatsResponse> => {
    const response = await apiClient.get<SensorStatsResponse>('/sensor-data/stats', { params });
    return response.data;
  },

  // Get metadata: Devices
  getDevices: async (): Promise<string[]> => {
    const response = await apiClient.get<string[]>('/metadata/devices');
    return response.data;
  },

  // Get metadata: Sensor Types
  getSensorTypes: async (): Promise<string[]> => {
    const response = await apiClient.get<string[]>('/metadata/sensor-types');
    return response.data;
  },

  // Get metadata: Locations
  getLocations: async (): Promise<string[]> => {
    const response = await apiClient.get<string[]>('/metadata/locations');
    return response.data;
  },

  // Get metadata: Sensor IDs
  getSensorIds: async (): Promise<string[]> => {
    const response = await apiClient.get<string[]>('/metadata/sensor-ids');
    return response.data;
  },
}; 