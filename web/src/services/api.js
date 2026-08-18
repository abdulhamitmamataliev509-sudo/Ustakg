import axios from 'axios';

const API_BASE = 'http://localhost:8000/api/v1';

const api = axios.create({ baseURL: API_BASE, timeout: 10000 });

export const setAuthToken = (token) => {
  if (token) api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  else delete api.defaults.headers.common['Authorization'];
};

api.interceptors.request.use((cfg) => {
  if (!cfg.headers.Authorization && typeof window !== 'undefined') {
    const token = localStorage.getItem('token');
    if (token) cfg.headers.Authorization = `Bearer ${token}`;
  }
  return cfg;
});

api.interceptors.response.use((res) => res, (err) => {
  if (err.response && err.response.status === 401) {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('token');
    }
  }
  return Promise.reject(err);
});

export default api;
