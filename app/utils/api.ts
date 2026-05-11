import { $fetch } from 'ofetch';
import { adminConfig } from '../../admin.config';

class ApiClient {
  private baseURL: string;

  constructor() {
    this.baseURL = adminConfig.apiPrefix;
  }

  private getToken(): string | null {
    if (typeof window === 'undefined') {
      return null;
    }
    return localStorage.getItem('admin_token');
  }

  public setToken(token: string): void {
    if (typeof window !== 'undefined') {
      localStorage.setItem('admin_token', token);
    }
  }

  public clearToken(): void {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('admin_token');
    }
  }

  private async request<T>(url: string, options: any = {}): Promise<T> {
    const token = this.getToken();
    const headers: Record<string, string> = {
      ...options.headers,
    };

    if (token) {
      headers.Authorization = `Bearer ${token}`;
    }

    try {
      const response = await $fetch<T>(`${this.baseURL}${url}`, {
        ...options,
        headers,
      });
      return response as T;
    } catch (error: any) {
      if (error.status === 401) {
        this.clearToken();
        if (typeof window !== 'undefined') {
          window.location.href = '/admin/login';
        }
      }
      throw error;
    }
  }

  public async get<T>(url: string, config?: any): Promise<T> {
    return this.request<T>(url, {
      method: 'GET',
      query: config?.params,
      ...config,
    });
  }

  public async post<T>(url: string, data?: any, config?: any): Promise<T> {
    return this.request<T>(url, {
      method: 'POST',
      body: data,
      ...config,
    });
  }

  public async put<T>(url: string, data?: any, config?: any): Promise<T> {
    return this.request<T>(url, {
      method: 'PUT',
      body: data,
      ...config,
    });
  }

  public async delete<T>(url: string, config?: any): Promise<T> {
    return this.request<T>(url, {
      method: 'DELETE',
      ...config,
    });
  }

  public async upload<T>(url: string, formData: FormData): Promise<T> {
    return this.request<T>(url, {
      method: 'POST',
      body: formData,
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  }
}

export const apiClient = new ApiClient();
