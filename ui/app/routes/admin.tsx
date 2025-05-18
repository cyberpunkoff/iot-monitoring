import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router';
import { useAuth } from '../context/AuthContext';
import { deviceApi } from '../services/api';
import type { Device, DeviceCreate } from '../types/device';
import ProtectedRoute from "../components/ProtectedRoute";

function AdminPage() {
  const { isAdmin, isLoggedIn } = useAuth();
  const navigate = useNavigate();
  const [devices, setDevices] = useState<Device[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showAddForm, setShowAddForm] = useState(false);
  const [formData, setFormData] = useState<DeviceCreate>({
    device_id: '',
    name: '',
    location: '',
    description: ''
  });

  useEffect(() => {
    if (!isLoading && (!isLoggedIn || !isAdmin)) {
      navigate('/');
    }
  }, [isAdmin, isLoggedIn, navigate, isLoading]);

  useEffect(() => {
    const loadDevices = async () => {
      try {
        setIsLoading(true);
        const response = await deviceApi.getAllDevices();
        setDevices(response.data);
      } catch (err: any) {
        console.error('Error loading devices:', err);
        setError('Не удалось загрузить устройства. Пожалуйста, попробуйте позже.');
      } finally {
        setIsLoading(false);
      }
    };

    loadDevices();
  }, []);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    
    try {
      const newDevice = await deviceApi.createDevice(formData);
      setDevices(prev => [...prev, newDevice]);
      setShowAddForm(false);
      setFormData({
        device_id: '',
        name: '',
        location: '',
        description: ''
      });
    } catch (err: any) {
      console.error('Error creating device:', err);
      setError(err.response?.data?.detail || 'Не удалось создать устройство. Пожалуйста, проверьте данные и попробуйте еще раз.');
    }
  };

  const handleDelete = async (deviceId: string) => {
    if (window.confirm('Вы уверены, что хотите удалить это устройство?')) {
      try {
        await deviceApi.deleteDevice(deviceId);
        setDevices(prev => prev.filter(device => device.device_id !== deviceId));
      } catch (err: any) {
        console.error('Error deleting device:', err);
        setError(err.response?.data?.detail || 'Не удалось удалить устройство. Пожалуйста, попробуйте позже.');
      }
    }
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-[500px]">
        <div className="text-center">
          <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-indigo-600 border-r-transparent align-[-0.125em]"></div>
          <p className="mt-4 text-gray-600 dark:text-gray-400">Загрузка...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-6">
      <h1 className="text-3xl font-bold mb-8">Управление устройствами</h1>
      
      {error && (
        <div className="mb-6 rounded-md bg-red-50 p-4 text-sm text-red-700 dark:bg-red-900/30 dark:text-red-400">
          {error}
        </div>
      )}
      
      <div className="mb-6">
        <button
          onClick={() => setShowAddForm(!showAddForm)}
          className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-md"
        >
          {showAddForm ? 'Отменить' : 'Добавить новое устройство'}
        </button>
      </div>
      
      {showAddForm && (
        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md mb-8">
          <h2 className="text-xl font-semibold mb-4">Добавить новое устройство</h2>
          <form onSubmit={handleSubmit}>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
              <div>
                <label htmlFor="device_id" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  ID устройства*
                </label>
                <input
                  id="device_id"
                  name="device_id"
                  type="text"
                  required
                  className="w-full rounded-md border-0 py-2 px-3 text-gray-900 ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-indigo-600 dark:bg-gray-700 dark:text-white dark:ring-gray-600"
                  value={formData.device_id}
                  onChange={handleChange}
                  placeholder="device-001"
                />
              </div>
              <div>
                <label htmlFor="name" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Название устройства*
                </label>
                <input
                  id="name"
                  name="name"
                  type="text"
                  required
                  className="w-full rounded-md border-0 py-2 px-3 text-gray-900 ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-indigo-600 dark:bg-gray-700 dark:text-white dark:ring-gray-600"
                  value={formData.name}
                  onChange={handleChange}
                  placeholder="Датчик температуры 1"
                />
              </div>
              <div>
                <label htmlFor="location" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Местоположение
                </label>
                <input
                  id="location"
                  name="location"
                  type="text"
                  className="w-full rounded-md border-0 py-2 px-3 text-gray-900 ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-indigo-600 dark:bg-gray-700 dark:text-white dark:ring-gray-600"
                  value={formData.location}
                  onChange={handleChange}
                  placeholder="Комната 123"
                />
              </div>
              <div>
                <label htmlFor="description" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Описание
                </label>
                <textarea
                  id="description"
                  name="description"
                  rows={3}
                  className="w-full rounded-md border-0 py-2 px-3 text-gray-900 ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-indigo-600 dark:bg-gray-700 dark:text-white dark:ring-gray-600"
                  value={formData.description}
                  onChange={handleChange}
                  placeholder="Описание устройства..."
                />
              </div>
            </div>
            <div className="flex justify-end">
              <button
                type="button"
                onClick={() => setShowAddForm(false)}
                className="bg-gray-200 hover:bg-gray-300 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300 px-4 py-2 rounded-md mr-2"
              >
                Отмена
              </button>
              <button
                type="submit"
                className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-md"
              >
                Сохранить
              </button>
            </div>
          </form>
        </div>
      )}
      
      <div className="bg-white dark:bg-gray-800 overflow-hidden shadow-md rounded-lg">
        <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <thead className="bg-gray-50 dark:bg-gray-700">
            <tr>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">ID</th>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Название</th>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Местоположение</th>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Статус</th>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Действия</th>
            </tr>
          </thead>
          <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
            {devices.length === 0 ? (
              <tr>
                <td colSpan={5} className="px-6 py-4 text-center text-gray-500 dark:text-gray-400">
                  Устройства не найдены. Добавьте новое устройство.
                </td>
              </tr>
            ) : (
              devices.map((device) => (
                <tr key={device.device_id}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">{device.device_id}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-300">{device.name}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-300">{device.location || '—'}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${device.is_active 
                      ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400' 
                      : 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400'}`}
                    >
                      {device.is_active ? 'Активно' : 'Неактивно'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-300">
                    <button
                      onClick={() => handleDelete(device.device_id)}
                      className="text-red-600 hover:text-red-900 dark:text-red-400 dark:hover:text-red-300"
                    >
                      Удалить
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default function ProtectedAdminPage() {
  return (
    <ProtectedRoute requireAdmin={true}>
      <AdminPage />
    </ProtectedRoute>
  );
}
