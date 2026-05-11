import { defineStore } from 'pinia';
import type { AdminUser, LoginCredentials } from '~/types/admin';
import { apiClient } from '~/utils/api';

interface LoginResponse {
  success: boolean;
  data: {
    token: string;
    admin: AdminUser;
  };
}

interface AdminState {
  user: AdminUser | null;
  token: string | null;
  loading: boolean;
  error: string | null;
}

export const useAdminStore = defineStore('admin', {
  state: (): AdminState => ({
    user: null,
    token: null,
    loading: false,
    error: null,
  }),

  getters: {
    isAuthenticated: (state) => !!state.token,
    currentUser: (state) => state.user,
    isLoading: (state) => state.loading,
    errorState: (state) => state.error,
  },

  actions: {
    async login(credentials: LoginCredentials) {
      this.loading = true;
      this.error = null;

      try {
        const response = await apiClient.post<LoginResponse>(
          '/auth/login',
          credentials
        );

        if (response.success) {
          this.setToken(response.data.token);
          this.user = response.data.admin;
          return { success: true };
        } else {
          throw new Error('登录失败');
        }
      } catch (error: any) {
        this.error = error.response?.data?.message || '登录失败，请检查用户名和密码';
        return { success: false, error: this.error };
      } finally {
        this.loading = false;
      }
    },

    async fetchCurrentUser() {
      try {
        const response = await apiClient.get<any>('/auth/me');
        if (response.success) {
          this.user = response.data;
        } else {
          this.user = null;
        }
      } catch (error) {
        this.user = null;
      }
    },

    logout() {
      this.token = null;
      this.user = null;
      this.error = null;
      apiClient.clearToken();
    },

    setToken(token: string) {
      this.token = token;
      apiClient.setToken(token);
    },

    clearError() {
      this.error = null;
    },
  },
});
