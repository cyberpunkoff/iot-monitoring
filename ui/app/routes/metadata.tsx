import { useState, useEffect } from "react";
import { api } from "../services/api";
import ProtectedRoute from "../components/ProtectedRoute";

export function meta() {
  return [
    { title: "Метаданные - Панель IoT датчиков" },
    { name: "description", content: "Просмотр метаданных для ваших IoT датчиков" },
  ];
}

function Metadata() {
  const [devices, setDevices] = useState<string[]>([]);
  const [sensorTypes, setSensorTypes] = useState<string[]>([]);
  const [locations, setLocations] = useState<string[]>([]);
  const [sensorIds, setSensorIds] = useState<string[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  
  // Load metadata
  useEffect(() => {
    const fetchMetadata = async () => {
      setLoading(true);
      setError(null);
      
      try {
        const [devicesData, sensorTypesData, locationsData, sensorIdsData] = await Promise.all([
          api.getDevices(),
          api.getSensorTypes(),
          api.getLocations(),
          api.getSensorIds()
        ]);
        
        setDevices(devicesData);
        setSensorTypes(sensorTypesData);
        setLocations(locationsData);
        setSensorIds(sensorIdsData);
      } catch (err) {
        setError("Не удалось загрузить метаданные. Пожалуйста, попробуйте снова.");
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    
    fetchMetadata();
  }, []);
  
  // Render loading state
  if (loading) {
    return (
      <div>
        <div className="mb-6">
          <h1 className="text-2xl font-bold mb-2">Метаданные датчиков</h1>
          <p className="text-gray-600 dark:text-gray-400">
            Просмотр доступных устройств, типов датчиков и расположений
          </p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6 animate-pulse">
              <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/3 mb-4"></div>
              <div className="space-y-2">
                <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded"></div>
                <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-5/6"></div>
                <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-4/6"></div>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }
  
  // Show error if needed
  if (error) {
    return (
      <div>
        <div className="mb-6">
          <h1 className="text-2xl font-bold mb-2">Метаданные датчиков</h1>
          <p className="text-gray-600 dark:text-gray-400">
            Просмотр доступных устройств, типов датчиков и расположений
          </p>
        </div>
        
        <div className="p-4 text-red-700 bg-red-100 dark:bg-red-900 dark:text-red-200 rounded-lg">
          {error}
        </div>
      </div>
    );
  }
  
  // Render metadata
  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold mb-2">Метаданные датчиков</h1>
        <p className="text-gray-600 dark:text-gray-400">
          Просмотр доступных устройств, типов датчиков и расположений
        </p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Devices */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
          <h2 className="text-lg font-medium mb-4">Устройства ({devices.length})</h2>
          {devices.length === 0 ? (
            <p className="text-gray-500 dark:text-gray-400">Нет доступных устройств.</p>
          ) : (
            <ul className="divide-y divide-gray-200 dark:divide-gray-700">
              {devices.map((device) => (
                <li key={device} className="py-2">
                  {device}
                </li>
              ))}
            </ul>
          )}
        </div>
        
        {/* Sensor Types */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
          <h2 className="text-lg font-medium mb-4">Типы датчиков ({sensorTypes.length})</h2>
          {sensorTypes.length === 0 ? (
            <p className="text-gray-500 dark:text-gray-400">Нет доступных типов датчиков.</p>
          ) : (
            <ul className="divide-y divide-gray-200 dark:divide-gray-700">
              {sensorTypes.map((type) => (
                <li key={type} className="py-2">
                  {type}
                </li>
              ))}
            </ul>
          )}
        </div>
        
        {/* Locations */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
          <h2 className="text-lg font-medium mb-4">Расположения ({locations.length})</h2>
          {locations.length === 0 ? (
            <p className="text-gray-500 dark:text-gray-400">Нет доступных расположений.</p>
          ) : (
            <ul className="divide-y divide-gray-200 dark:divide-gray-700">
              {locations.map((location) => (
                <li key={location} className="py-2">
                  {location}
                </li>
              ))}
            </ul>
          )}
        </div>
        
        {/* Sensor IDs */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
          <h2 className="text-lg font-medium mb-4">ID датчиков ({sensorIds.length})</h2>
          {sensorIds.length === 0 ? (
            <p className="text-gray-500 dark:text-gray-400">Нет доступных ID датчиков.</p>
          ) : (
            <ul className="divide-y divide-gray-200 dark:divide-gray-700">
              {sensorIds.map((id) => (
                <li key={id} className="py-2">
                  {id}
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
}

export default function ProtectedMetadata() {
  return (
    <ProtectedRoute>
      <Metadata />
    </ProtectedRoute>
  );
} 