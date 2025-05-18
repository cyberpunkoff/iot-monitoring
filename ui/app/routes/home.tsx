import { useState, useEffect } from "react";
import type { Route } from "./+types/home";
import { api, type SensorData } from "../services/api";
import FilterControls from "../components/FilterControls";
import SensorDataTable from "../components/SensorDataTable";
import ProtectedRoute from "../components/ProtectedRoute";

export function meta({}: Route.MetaArgs) {
  return [
    { title: "Панель IoT датчиков" },
    { name: "description", content: "Мониторинг данных IoT датчиков в реальном времени" },
  ];
}

function Home() {
  const [sensorData, setSensorData] = useState<SensorData[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [totalCount, setTotalCount] = useState<number>(0);
  
  const [filters, setFilters] = useState<{
    deviceId?: string;
    sensorType?: string;
    location?: string;
  }>({});
  
  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);
      
      try {
        const response = await api.getLatestSensorData({
          device_id: filters.deviceId,
          sensor_type: filters.sensorType,
          location: filters.location,
          limit: 100
        });
        
        setSensorData(response.data);
        setTotalCount(response.total_count);
      } catch (err) {
        setError("Не удалось загрузить данные датчиков. Пожалуйста, попробуйте снова.");
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    
    fetchData();
    
    const refreshInterval = setInterval(fetchData, 30000);
    
    return () => clearInterval(refreshInterval);
  }, [filters]);
  
  const handleFilterChange = (newFilters: {
    deviceId?: string;
    sensorType?: string;
    location?: string;
  }) => {
    setFilters(newFilters);
  };
  
  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold mb-2">Последние показания датчиков</h1>
        <p className="text-gray-600 dark:text-gray-400">
          Просмотр самых последних данных с ваших IoT устройств
        </p>
      </div>
      
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

export default function ProtectedHome() {
  return (
    <ProtectedRoute>
      <Home />
    </ProtectedRoute>
  );
}
