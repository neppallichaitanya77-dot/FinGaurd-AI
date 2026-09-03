import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
});

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('finguard_token');
    if (token) config.headers.Authorization = `Bearer ${token}`;
    return config;
  },
  (error) => Promise.reject(error)
);

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('finguard_token');
      localStorage.removeItem('finguard_user');
      if (typeof window !== 'undefined' && !['/login', '/register'].includes(window.location.pathname)) {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export const authAPI = {
  login: (credentials) => api.post('/auth/login', credentials),
  register: (data) => api.post('/auth/register', data),
  logout: () => api.post('/auth/logout'),
  getProfile: () => api.get('/auth/me'),
  updateProfile: (data) => api.put('/auth/profile', data),
};

export const dashboardAPI = {
  getSummary: () => api.get('/dashboard'),
};

export const financialHealthAPI = {
  getHealth: () => api.get('/financial-health'),
};

export const riskAPI = {
  getRiskScore: () => api.get('/risk-score'),
};

export const alertsAPI = {
  getAlerts: (params) => api.get('/alerts', { params }),
  markAsRead: (id) => api.put(`/alerts/${id}/read`),
  dismissAlert: (id) => api.delete(`/alerts/${id}`),
};

export const transactionsAPI = {
  getTransactions: (params) => api.get('/transactions', { params }),
};

export const loansAPI = {
  getLoans: () => api.get('/loans'),
  getLoanPayments: (id) => api.get(`/loans/${id}/payments`),
};

export const recommendationsAPI = {
  getRecommendations: () => api.get('/recommendations'),
  acceptRecommendation: (id) => api.post(`/recommendations/${id}/accept`),
  dismissRecommendation: (id) => api.post(`/recommendations/${id}/dismiss`),
};

export const aiAPI = {
  chat: (message, conversationId, previousSuggestedQuestions = []) => api.post('/ai/chat', {
    message,
    conversation_id: conversationId,
    previous_suggested_questions: previousSuggestedQuestions,
  }),
  getHistory: () => api.get('/ai/history'),
};

export const scenarioAPI = {
  analyze: (data) => api.post('/scenario/analyze', data),
};

export default api;
