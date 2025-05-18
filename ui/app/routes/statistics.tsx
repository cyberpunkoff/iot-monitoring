import { useState, useEffect } from "react";
import { api, type SensorStats } from "../services/api";
import FilterControls from "../components/FilterControls";
import SensorStatsTable from "../components/SensorStatsTable";
import DateRangePicker from "../components/DateRangePicker";
import ProtectedRoute from "../components/ProtectedRoute";

export function meta() {
  return [
    { title: "Статистика - Панель IoT датчиков" },
    { name: "description", content: "Просмотр статистики IoT-датчиков" },
  ];
}

function Statistics() {
  const [sensorStats, setSensorStats] = useState<SensorStats[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  
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
      date.setDate(date.getDate() - 30);
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
        const response = await api.getSensorStats({
          from_timestamp: dateRange.fromDate,
          to_timestamp: dateRange.toDate,
          device_id: filters.deviceId,
          sensor_type: filters.sensorType,
          location: filters.location
        });
        
        setSensorStats(response.data);
      } catch (err) {
        setError("Не удалось загрузить статистику. Пожалуйста, попробуйте снова.");
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
        <h1 className="text-2xl font-bold mb-2">Статистика датчиков</h1>
        <p className="text-gray-600 dark:text-gray-400">
          Просмотр агрегированной статистики для ваших IoT датчиков
        </p>
      </div>
      
      <DateRangePicker onDateRangeChange={handleDateRangeChange} />
      
      <FilterControls onFilterChange={handleFilterChange} />
      
      {error && (
        <div className="mb-6 p-4 text-red-700 bg-red-100 dark:bg-red-900 dark:text-red-200 rounded-lg">
          {error}
        </div>
      )}
      
      <SensorStatsTable data={sensorStats} loading={loading} />
    </div>
  );
}

export default function ProtectedStatistics() {
  return (
    <ProtectedRoute>
      <Statistics />
    </ProtectedRoute>
  );
}
