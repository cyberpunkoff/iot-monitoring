import axios from 'axios';
import type { InternalAxiosRequestConfig } from 'axios';
import type { AuthTokens, LoginCredentials, RegisterData, User } from '../types/auth';
import type { Device, DeviceCreate, DeviceResponse } from '../types/device';

const API_BASE_URL = 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

apiClient.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = localStorage.getItem('token');
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

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

export const authApi = {
  register: async (userData: RegisterData): Promise<User> => {
    const response = await apiClient.post<User>('/auth/register', userData);
    return response.data;
  },

  login: async (credentials: LoginCredentials): Promise<AuthTokens> => {
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
    
    if (response.data.access_token) {
      localStorage.setItem('token', response.data.access_token);
    }
    
    return response.data;
  },

  getCurrentUser: async (): Promise<User> => {
    const response = await apiClient.get<User>('/auth/me');
    return response.data;
  },

  logout: (): void => {
    localStorage.removeItem('token');
  },
};

export const deviceApi = {
  getAllDevices: async (): Promise<DeviceResponse> => {
    const response = await apiClient.get<DeviceResponse>('/devices');
    return response.data;
  },

  getDevice: async (deviceId: string): Promise<Device> => {
    const response = await apiClient.get<Device>(`/devices/${deviceId}`);
    return response.data;
  },

  createDevice: async (deviceData: DeviceCreate): Promise<Device> => {
    const response = await apiClient.post<Device>('/devices', deviceData);
    return response.data;
  },

  updateDevice: async (deviceId: string, deviceData: Partial<DeviceCreate>): Promise<Device> => {
    const response = await apiClient.put<Device>(`/devices/${deviceId}`, deviceData);
    return response.data;
  },

  deleteDevice: async (deviceId: string): Promise<void> => {
    await apiClient.delete(`/devices/${deviceId}`);
  },
};

export const api = {
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

  getDevices: async (): Promise<string[]> => {
    const response = await apiClient.get<string[]>('/metadata/devices');
    return response.data;
  },

  getSensorTypes: async (): Promise<string[]> => {
    const response = await apiClient.get<string[]>('/metadata/sensor-types');
    return response.data;
  },

  getLocations: async (): Promise<string[]> => {
    const response = await apiClient.get<string[]>('/metadata/locations');
    return response.data;
  },

  getSensorIds: async (): Promise<string[]> => {
    const response = await apiClient.get<string[]>('/metadata/sensor-ids');
    return response.data;
  },
};
