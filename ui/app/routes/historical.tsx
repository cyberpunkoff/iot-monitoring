import { useState, useEffect } from "react";
import type { Route } from "./+types/historical";
import { api, type SensorData } from "../services/api";
import FilterControls from "../components/FilterControls";
import SensorDataTable from "../components/SensorDataTable";
import DateRangePicker from "../components/DateRangePicker";
import ProtectedRoute from "../components/ProtectedRoute";

export function meta({}: Route.MetaArgs) {
  return [
    { title: "Исторические данные - Панель IoT датчиков" },
    { name: "description", content: "Просмотр исторических данных IoT датчиков" },
  ];
}

function Historical() {
  const [sensorData, setSensorData] = useState<SensorData[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [totalCount, setTotalCount] = useState<number>(0);
  
  const [filters, setFilters] = useState<{
    deviceId?: string;
    sensorType?: string;
    location?: string;
  }>({});
  
  const [dateRange, setDateRange] = useState<{
    fromDate: string;
    toDate: string;
  }>({
    fromDate: (() => {
      const date = new Date();
      date.setDate(date.getDate() - 7);
      date.setHours(0, 0, 0, 0);
      return date.toISOString();
    })(),
    toDate: (() => {
      const date = new Date();
      date.setHours(23, 59, 59, 999);
      return date.toISOString();
    })(),
  });
  
  useEffect(() => {
    if (!dateRange.fromDate || !dateRange.toDate) return;
    
    const fetchData = async () => {
      setLoading(true);
      setError(null);
      
      try {
        const response = await api.getHistoricalSensorData({
          from_timestamp: dateRange.fromDate,
          to_timestamp: dateRange.toDate,
          device_id: filters.deviceId,
          sensor_type: filters.sensorType,
          location: filters.location,
          limit: 1000
        });
        
        setSensorData(response.data);
        setTotalCount(response.total_count);
      } catch (err) {
        setError("Не удалось загрузить исторические данные. Пожалуйста, попробуйте снова.");
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    
    fetchData();
  }, [filters, dateRange]);
  
  const handleFilterChange = (newFilters: {
    deviceId?: string;
    sensorType?: string;
    location?: string;
  }) => {
    setFilters(newFilters);
  };
  
  const handleDateRangeChange = (fromDate: string, toDate: string) => {
    setDateRange({ fromDate, toDate });
  };
  
  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold mb-2">Исторические данные датчиков</h1>
        <p className="text-gray-600 dark:text-gray-400">
          Просмотр показаний датчиков в выбранном временном диапазоне
        </p>
      </div>
      
      <DateRangePicker onDateRangeChange={handleDateRangeChange} />
      
      <FilterControls onFilterChange={handleFilterChange} />
      
      {error && (
        <div className="mb-6 p-4 text-red-700 bg-red-100 dark:bg-red-900 dark:text-red-200 rounded-lg">
          {error}
        </div>
      )}
      
      <div className="mb-4 text-sm text-gray-600 dark:text-gray-400">
        {!loading && `Показано ${sensorData.length} из ${totalCount} показаний`}
      </div>
      
      <SensorDataTable data={sensorData} loading={loading} />
    </div>
  );
}

export default function ProtectedHistorical() {
  return (
    <ProtectedRoute>
      <Historical />
    </ProtectedRoute>
  );
}
