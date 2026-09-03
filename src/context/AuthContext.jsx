import { createContext, useContext, useState, useEffect } from 'react';
import { authAPI } from '../services/api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('finguard_token'));
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const storedUser = localStorage.getItem('finguard_user');
    if (token && storedUser) {
      try {
        setUser(JSON.parse(storedUser));
      } catch {
        logout();
      }
    }
    setLoading(false);
  }, []);

  const login = async (email, password) => {
    const response = await authAPI.login({ email, password });
    const data = response.data;
    const access_token = data.access_token || data.token;
    const userData = data.user || data;
    localStorage.setItem('finguard_token', access_token);
    localStorage.setItem('finguard_user', JSON.stringify(userData));
    setToken(access_token);
    setUser(userData);
    return data;
  };

  const register = async (name, email, password) => {
    const response = await authAPI.register({ name, email, password });
    const data = response.data;
    const access_token = data.access_token || data.token;
    const userData = data.user || data;
    localStorage.setItem('finguard_token', access_token);
    localStorage.setItem('finguard_user', JSON.stringify(userData));
    setToken(access_token);
    setUser(userData);
    return data;
  };

  const logout = () => {
    authAPI.logout().catch(() => {});
    localStorage.removeItem('finguard_token');
    localStorage.removeItem('finguard_user');
    setToken(null);
    setUser(null);
  };

  const updateUser = (userData) => {
    setUser(userData);
    localStorage.setItem('finguard_user', JSON.stringify(userData));
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        loading,
        login,
        register,
        logout,
        updateUser,
        isAuthenticated: !!token,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within an AuthProvider');
  return context;
}
