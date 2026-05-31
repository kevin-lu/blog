import axios, {
  type AxiosInstance,
  type AxiosRequestConfig,
  type AxiosError,
  type InternalAxiosRequestConfig,
} from 'axios'
import { useMessage } from 'naive-ui'

// 扩展 AxiosRequestConfig 类型，添加重试标记
interface RetryableConfig extends InternalAxiosRequestConfig {
  _retry?: boolean
}

// API 错误码
const API_ERRORS = {
  NETWORK_ERROR: '网络连接失败，请检查网络设置',
  TIMEOUT: '请求超时，请重试',
  UNAUTHORIZED: '登录已过期，请重新登录',
  FORBIDDEN: '无权访问此资源',
  NOT_FOUND: '请求的资源不存在',
  SERVER_ERROR: '服务器错误，请稍后重试',
  UNKNOWN: '发生未知错误',
}

// 获取 message 实例
const message = useMessage()

class ApiClient {
  private client: AxiosInstance
  private maxRetries = 2
  private retryDelay = 1000 // ms

  constructor() {
    const baseURL = (import.meta as any).env.VITE_API_BASE_URL || '/api/v1'

    this.client = axios.create({
      baseURL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    this.setupInterceptors()
  }

  private setupInterceptors() {
    // Request interceptor
    this.client.interceptors.request.use(
      (config: RetryableConfig) => {
        const token = localStorage.getItem('access_token')
        if (token) {
          config.headers.Authorization = `Bearer ${token}`
        }
        return config
      },
      (error) => Promise.reject(error)
    )

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => response,
      async (error: AxiosError) => {
        const originalRequest = error.config as RetryableConfig | undefined

        // 获取错误信息
        const errorMessage = this.getErrorMessage(error)

        // 401 错误处理 - Token 刷新
        if (error.response?.status === 401 && originalRequest && !originalRequest._retry) {
          originalRequest._retry = true

          try {
            const refreshToken = localStorage.getItem('refresh_token')
            if (!refreshToken) {
              throw new Error('No refresh token')
            }

            const response = await axios.post(
              `${this.client.defaults.baseURL}/auth/refresh`,
              {},
              {
                headers: {
                  Authorization: `Bearer ${refreshToken}`,
                },
              }
            )

            const newAccessToken = response.data.access_token
            localStorage.setItem('access_token', newAccessToken)

            // Retry original request with new token
            if (originalRequest.headers) {
              originalRequest.headers.Authorization = `Bearer ${newAccessToken}`
            }
            return this.client(originalRequest)
          } catch (refreshError) {
            // Refresh failed, logout
            localStorage.removeItem('access_token')
            localStorage.removeItem('refresh_token')
            message.error('登录已过期，请重新登录')
            window.location.href = '/admin/login'
            return Promise.reject(refreshError)
          }
        }

        // 其他错误显示提示
        if (originalRequest && !originalRequest._retry) {
          message.error(errorMessage)
        }

        return Promise.reject(error)
      }
    )
  }

  /**
   * 获取错误信息
   */
  private getErrorMessage(error: AxiosError): string {
    if (!error.response) {
      return error.message === 'Network Error'
        ? API_ERRORS.NETWORK_ERROR
        : API_ERRORS.UNKNOWN
    }

    const status = error.response.status

    switch (status) {
      case 401:
        return API_ERRORS.UNAUTHORIZED
      case 403:
        return API_ERRORS.FORBIDDEN
      case 404:
        return API_ERRORS.NOT_FOUND
      case 500:
      case 502:
      case 503:
        return API_ERRORS.SERVER_ERROR
      default:
        // 从响应中获取具体错误信息
        const data = error.response.data as any
        return data?.message || data?.error || API_ERRORS.UNKNOWN
    }
  }

  /**
   * 延迟函数
   */
  private delay(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms))
  }

  /**
   * 带重试的 GET 请求
   */
  async get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    return this.requestWithRetry<T>('get', url, undefined, config)
  }

  /**
   * 带重试的 POST 请求
   */
  async post<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    return this.requestWithRetry<T>('post', url, data, config)
  }

  /**
   * 带重试的 PUT 请求
   */
  async put<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    return this.requestWithRetry<T>('put', url, data, config)
  }

  /**
   * 带重试的 DELETE 请求
   */
  async delete<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    return this.requestWithRetry<T>('delete', url, undefined, config)
  }

  /**
   * 通用重试逻辑
   */
  private async requestWithRetry<T>(
    method: 'get' | 'post' | 'put' | 'delete',
    url: string,
    data?: any,
    config?: AxiosRequestConfig,
    retryCount = 0
  ): Promise<T> {
    try {
      const baseURL = String(this.client.defaults.baseURL || '').replace(/\/$/, '')
      const path = url.replace(/^\//, '')
      const fullUrl = `${baseURL}/${path}`
      console.log(`[API Request] ${method.toUpperCase()} ${fullUrl}`)
      
      if (method === 'get' || method === 'delete') {
        const response = await this.client[method]<T>(url, config)
        return response.data
      } else {
        const response = await this.client[method]<T>(url, data, config)
        return response.data
      }
    } catch (error: any) {
      // 如果是网络错误或 5xx 错误，尝试重试
      const shouldRetry =
        !error.response ||
        error.response.status >= 500 ||
        error.code === 'ECONNABORTED'

      if (shouldRetry && retryCount < this.maxRetries) {
        console.log(`Request retry ${retryCount + 1}/${this.maxRetries} for ${url}`)
        await this.delay(this.retryDelay * (retryCount + 1))
        return this.requestWithRetry<T>(method, url, data, config, retryCount + 1)
      }

      throw error
    }
  }
}

export const apiClient = new ApiClient()
