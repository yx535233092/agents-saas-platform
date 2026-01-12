import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { User } from '@/types/user';
import { authService } from '@/services/auth';

interface AuthState {
  accessToken: string | null;
  user: User | null;
  isAuthenticated: boolean;

  setToken: (token: string) => void;
  setUser: (user: User) => void;
  logout: () => Promise<void>;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      accessToken: null,
      user: null,
      isAuthenticated: false,

      setToken: (token) =>
        set({
          accessToken: token,
          isAuthenticated: true
        }),

      setUser: (user) => set({ user }),

      logout: async () => {
        // 尝试调用统一认证系统的logout API
        try {
          await authService.logout();
        } catch (error) {
          // 即使logout API调用失败，也继续清除本地状态
          console.error('Logout API call failed:', error);
        }
        
        // 清除本地状态
        set({
          accessToken: null,
          user: null,
          isAuthenticated: false
        });
        localStorage.removeItem('auth-storage'); // Force clear persistence
      }
    }),
    {
      name: 'auth-storage'
    }
  )
);
