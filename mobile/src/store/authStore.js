import create from 'zustand';
import AsyncStorage from '@react-native-async-storage/async-storage';
import api, { setAuthToken } from '../services/api';

export const useAuthStore = create((set, get) => ({
  user: null,
  token: null,
  role: null,
  restoring: true,

  login: async (email, password) => {
    const res = await api.post('/auth/login', { email, password });
    const { access_token, user } = res.data;
    await AsyncStorage.setItem('token', access_token);
    setAuthToken(access_token);
    set({ user, token: access_token, role: user.role ?? 'CUSTOMER' });
    return user;
  },

  register: async (payload) => {
    const res = await api.post('/auth/register', payload);
    const { access_token, user } = res.data;
    await AsyncStorage.setItem('token', access_token);
    setAuthToken(access_token);
    set({ user, token: access_token, role: user.role ?? payload.role ?? 'CUSTOMER' });
    return user;
  },

  logout: async () => {
    await AsyncStorage.removeItem('token');
    setAuthToken(null);
    set({ user: null, token: null, role: null });
  },

  restoreToken: async () => {
    try {
      const token = await AsyncStorage.getItem('token');
      if (token) {
        setAuthToken(token);
        // try fetch profile
        const res = await api.get('/auth/me');
        set({ token, user: res.data, role: res.data.role ?? 'CUSTOMER' });
      }
    } catch (e) {
      console.warn('restoreToken error', e.message);
    } finally {
      set({ restoring: false });
    }
  }
}));
