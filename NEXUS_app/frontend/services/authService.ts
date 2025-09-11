import api from './api';
import useAuthStore from '../store/authStore';

export const login = async (credentials: any) => {
  const { login } = useAuthStore.getState();
  const response = await api.post('/auth/login', credentials);
  const user = response.data;
  login(user);
  return user;
};

export const register = async (userInfo: any) => {
  const response = await api.post('/auth/register', userInfo);
  return response.data;
};

export const logout = () => {
  const { logout } = useAuthStore.getState();
  logout();
};
