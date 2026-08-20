import create from 'zustand';
import AsyncStorage from '@react-native-async-storage/async-storage';
import api, { setAuthToken } from '../services/api';

export const useAuthStore = create((set, get) => ({
  user: null,
  token: null,
  role: null,
  restoring: true,

  // Backend contract: OAuth2 form (username=phone_number, password)
  login: async (phoneNumber, password) => {
    const form = new URLSearchParams();
    form.append('username', phoneNumber);
    form.append('password', password);
    const res = await api.post('/auth/login', form.toString(), {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
    return get()._setSession(res.data);
  },

  // Backend contract: { phone_number, password, full_name, role }
  register: async (payload) => {
    const res = await api.post('/auth/register', {
      phone_number: payload.phone_number,
      password: payload.password,
      full_name: payload.full_name,
      role: payload.role,
    });
    return get()._setSession(res.data);
  },

  _setSession: async (data) => {
    const accessToken = data?.access_token;
    if (!accessToken) throw new Error('No access token in response');
    await AsyncStorage.setItem('token', accessToken);
    if (data.refresh_token) {
      await AsyncStorage.setItem('refresh_token', data.refresh_token);
    }
    setAuthToken(accessToken);
    // Backend returns only tokens — fetch the current user afterwards.
    const me = await api.get('/auth/me');
    set({ token: accessToken, user: me.data, role: me.data?.role ?? 'CUSTOMER' });
    return me.data;
  },

  logout: async () => {
    await AsyncStorage.removeItem('token');
    await AsyncStorage.removeItem('refresh_token');
    setAuthToken(null);
    set({ user: null, token: null, role: null });
  },

  restoreToken: async () => {
    try {
      const token = await AsyncStorage.getItem('token');
      if (token) {
        setAuthToken(token);
        const res = await api.get('/auth/me');
        set({ token, user: res.data, role: res.data?.role ?? 'CUSTOMER' });
      }
    } catch (e) {
      console.warn('restoreToken error', e.message);
    } finally {
      set({ restoring: false });
    }
  },
}));
