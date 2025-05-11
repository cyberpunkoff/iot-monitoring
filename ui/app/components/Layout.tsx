import { Link, Outlet, useLocation, useNavigate } from "react-router";
import { useAuth } from "../context/AuthContext";

export default function Layout() {
  const location = useLocation();
  const navigate = useNavigate();
  const { isLoggedIn, isAdmin, user, logout } = useAuth();
  
  const isActiveLink = (path: string) => {
    return location.pathname === path;
  };
  
  const handleLogout = () => {
    logout();
    navigate('/login');
  };
  
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-white">
      <header className="bg-indigo-600 text-white shadow-md">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold">Мониторинг IoT-устройств</h1>
          
          {isLoggedIn ? (
            <div className="flex items-center">
              <span className="mr-4">
                {user?.username} {isAdmin && <span className="text-xs bg-yellow-500 text-white px-2 py-1 rounded-full ml-1">Админ</span>}
              </span>
              <button 
                onClick={handleLogout}
                className="bg-indigo-700 hover:bg-indigo-800 text-white text-sm py-1 px-3 rounded"
              >
                Выйти
              </button>
            </div>
          ) : (
            <Link 
              to="/login"
              className="bg-indigo-700 hover:bg-indigo-800 text-white text-sm py-1 px-3 rounded"
            >
              Войти
            </Link>
          )}
        </div>
      </header>
      
      {isLoggedIn && (
        <nav className="bg-white dark:bg-gray-800 shadow-sm">
          <div className="container mx-auto px-4">
            <div className="flex space-x-6 overflow-x-auto py-3">
              <Link 
                to="/" 
                className={`font-medium ${isActiveLink('/') 
                  ? 'text-indigo-600 dark:text-indigo-400 border-b-2 border-indigo-600' 
                  : 'text-gray-700 dark:text-gray-300 hover:text-indigo-600 dark:hover:text-indigo-400'}`}
              >
                Панель управления
              </Link>
              <Link 
                to="/historical" 
                className={`font-medium ${isActiveLink('/historical') 
                  ? 'text-indigo-600 dark:text-indigo-400 border-b-2 border-indigo-600' 
                  : 'text-gray-700 dark:text-gray-300 hover:text-indigo-600 dark:hover:text-indigo-400'}`}
              >
                Исторические данные
              </Link>
              <Link 
                to="/statistics" 
                className={`font-medium ${isActiveLink('/statistics') 
                  ? 'text-indigo-600 dark:text-indigo-400 border-b-2 border-indigo-600' 
                  : 'text-gray-700 dark:text-gray-300 hover:text-indigo-600 dark:hover:text-indigo-400'}`}
              >
                Статистика
              </Link>
              <Link 
                to="/metadata" 
                className={`font-medium ${isActiveLink('/metadata') 
                  ? 'text-indigo-600 dark:text-indigo-400 border-b-2 border-indigo-600' 
                  : 'text-gray-700 dark:text-gray-300 hover:text-indigo-600 dark:hover:text-indigo-400'}`}
              >
                Метаданные
              </Link>
              {isAdmin && (
                <Link 
                  to="/admin" 
                  className={`font-medium ${isActiveLink('/admin') 
                    ? 'text-indigo-600 dark:text-indigo-400 border-b-2 border-indigo-600' 
                    : 'text-gray-700 dark:text-gray-300 hover:text-indigo-600 dark:hover:text-indigo-400'}`}
                >
                  Управление устройствами
                </Link>
              )}
            </div>
          </div>
        </nav>
      )}
      
      <main className="container mx-auto px-4 py-6">
        <Outlet />
      </main>
    </div>
  );
} 