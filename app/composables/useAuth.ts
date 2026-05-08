import { useRouter } from 'vue-router';
import { useAdminStore } from '~/stores/admin';

export function useAuth() {
  const router = useRouter();
  const adminStore = useAdminStore();

  const requireAuth = async () => {
    if (!adminStore.isAuthenticated) {
      // 尝试从 localStorage 恢复 token
      const token = localStorage.getItem('admin_token');
      if (token) {
        await adminStore.fetchCurrentUser();
      }
      
      if (!adminStore.isAuthenticated) {
        router.push('/admin/login');
        return false;
      }
    }
    return true;
  };

  const logout = async () => {
    adminStore.logout();
    router.push('/admin/login');
  };

  return {
    requireAuth,
    logout,
    isAuthenticated: adminStore.isAuthenticated,
    currentUser: adminStore.currentUser,
  };
}
