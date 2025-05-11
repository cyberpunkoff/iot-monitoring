import React, { createContext, useContext, useState, useEffect } from 'react';
import type { ReactNode } from 'react';
import { jwtDecode } from 'jwt-decode';
import { authApi } from '../services/api';
import type { User, DecodedToken, LoginCredentials, RegisterData } from '../types/auth';
import { UserRole } from '../types/auth';

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  error: string | null;
  isLoggedIn: boolean;
  isAdmin: boolean;
  login: (credentials: LoginCredentials) => Promise<void>;
  register: (userData: RegisterData) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Check if token is expired
  const isTokenExpired = (token: string): boolean => {
    try {
      const decoded = jwtDecode<DecodedToken>(token);
      // Check if expiration timestamp is before current time
      return decoded.exp * 1000 < Date.now();
    } catch (err) {
      return true;
    }
  };

  // Check for existing token and load user data on mount
  useEffect(() => {
    const initAuth = async () => {
      setIsLoading(true);
      setError(null);
      
      try {
        const token = localStorage.getItem('token');
        
        if (!token || isTokenExpired(token)) {
          // Token is missing or expired, clear storage
          localStorage.removeItem('token');
          setUser(null);
          setIsLoading(false);
          return;
        }
        
        // Token exists and is valid, load user data
        const userData = await authApi.getCurrentUser();
        setUser(userData);
      } catch (err) {
        console.error('Authentication error:', err);
        localStorage.removeItem('token');
        setError('Authentication failed. Please log in again.');
      } finally {
        setIsLoading(false);
      }
    };
    
    initAuth();
  }, []);

  // Login handler
  const login = async (credentials: LoginCredentials) => {
    setIsLoading(true);
    setError(null);
    
    try {
      // First, get token by logging in
      await authApi.login(credentials);
      
      // Then get current user data
      const userData = await authApi.getCurrentUser();
      setUser(userData);
    } catch (err: any) {
      console.error('Login error:', err);
      setError(err.response?.data?.detail || 'Login failed. Please check your credentials.');
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  // Register handler
  const register = async (userData: RegisterData) => {
    setIsLoading(true);
    setError(null);
    
    try {
      // Register the user
      await authApi.register(userData);
      
      // After successful registration, log in with new credentials
      await login({
        username: userData.username,
        password: userData.password
      });
    } catch (err: any) {
      console.error('Registration error:', err);
      setError(err.response?.data?.detail || 'Registration failed. Please try again.');
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  // Logout handler
  const logout = () => {
    authApi.logout();
    setUser(null);
  };

  const isLoggedIn = user !== null;
  const isAdmin = user?.role === UserRole.ADMIN;

  const value = {
    user,
    isLoading,
    error,
    isLoggedIn,
    isAdmin,
    login,
    register,
    logout
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}; 