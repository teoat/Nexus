import {create} from 'zustand';

interface AuthState {
  isAuthenticated: boolean;
  user: any; // Replace 'any' with a proper user type
  login: (user: any) => void;
  logout: () => void;
}

const useAuthStore = create<AuthState>((set) => ({
  isAuthenticated: false,
  user: null,
  login: (user) => set({ isAuthenticated: true, user }),
  logout: () => set({ isAuthenticated: false, user: null }),
}));

export default useAuthStore;
