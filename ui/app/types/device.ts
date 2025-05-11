export interface Device {
  device_id: string;
  name: string;
  location?: string;
  description?: string;
  created_at: string;
  is_active: boolean;
}

export interface DeviceCreate {
  device_id: string;
  name: string;
  location?: string;
  description?: string;
}

export interface DeviceResponse {
  data: Device[];
  total_count: number;
} 