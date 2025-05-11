import { useEffect, useState } from "react";
import { api } from "../services/api";

interface FilterControlsProps {
  onFilterChange: (filters: {
    deviceId?: string;
    sensorType?: string;
    location?: string;
  }) => void;
  showReset?: boolean;
}

export default function FilterControls({ onFilterChange, showReset = true }: FilterControlsProps) {
  const [devices, setDevices] = useState<string[]>([]);
  const [sensorTypes, setSensorTypes] = useState<string[]>([]);
  const [locations, setLocations] = useState<string[]>([]);
  
  const [selectedDevice, setSelectedDevice] = useState<string>("");
  const [selectedSensorType, setSelectedSensorType] = useState<string>("");
  const [selectedLocation, setSelectedLocation] = useState<string>("");
  
  // Load filter options
  useEffect(() => {
    const loadFilterOptions = async () => {
      try {
        const [devicesData, sensorTypesData, locationsData] = await Promise.all([
          api.getDevices(),
          api.getSensorTypes(),
          api.getLocations()
        ]);
        
        setDevices(devicesData);
        setSensorTypes(sensorTypesData);
        setLocations(locationsData);
      } catch (error) {
        console.error("Error loading filter options:", error);
      }
    };
    
    loadFilterOptions();
  }, []);
  
  // Apply filters
  const applyFilters = () => {
    onFilterChange({
      deviceId: selectedDevice || undefined,
      sensorType: selectedSensorType || undefined,
      location: selectedLocation || undefined
    });
  };
  
  // Reset filters
  const resetFilters = () => {
    setSelectedDevice("");
    setSelectedSensorType("");
    setSelectedLocation("");
    onFilterChange({});
  };
  
  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-4 mb-6">
      <h2 className="text-lg font-medium mb-4">Фильтрация данных</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
        <div>
          <label htmlFor="device-select" className="block text-sm font-medium mb-1">
            Устройство
          </label>
          <select
            id="device-select"
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            value={selectedDevice}
            onChange={(e) => setSelectedDevice(e.target.value)}
          >
            <option value="">Все устройства</option>
            {devices.map((device) => (
              <option key={device} value={device}>
                {device}
              </option>
            ))}
          </select>
        </div>
        
        <div>
          <label htmlFor="sensor-type-select" className="block text-sm font-medium mb-1">
            Тип датчика
          </label>
          <select
            id="sensor-type-select"
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            value={selectedSensorType}
            onChange={(e) => setSelectedSensorType(e.target.value)}
          >
            <option value="">Все типы</option>
            {sensorTypes.map((type) => (
              <option key={type} value={type}>
                {type}
              </option>
            ))}
          </select>
        </div>
        
        <div>
          <label htmlFor="location-select" className="block text-sm font-medium mb-1">
            Расположение
          </label>
          <select
            id="location-select"
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            value={selectedLocation}
            onChange={(e) => setSelectedLocation(e.target.value)}
          >
            <option value="">Все расположения</option>
            {locations.map((location) => (
              <option key={location} value={location}>
                {location}
              </option>
            ))}
          </select>
        </div>
      </div>
      
      <div className="flex justify-end space-x-2">
        {showReset && (
          <button
            type="button"
            onClick={resetFilters}
            className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md hover:bg-gray-50 dark:hover:bg-gray-600"
          >
            Сбросить
          </button>
        )}
        <button
          type="button"
          onClick={applyFilters}
          className="px-4 py-2 text-sm font-medium text-white bg-indigo-600 border border-transparent rounded-md hover:bg-indigo-700 focus:outline-none"
        >
          Применить фильтры
        </button>
      </div>
    </div>
  );
} 