const DEFAULT_API_TARGET = 'http://127.0.0.1:5001'

const SERVER_ASSET_PREFIXES = ['/uploads/', '/images/', '/documents/']

const isAbsoluteUrl = (value: string) => /^(?:[a-z]+:)?\/\//i.test(value)

const getApiTarget = () => {
  const configured = (import.meta as any).env.VITE_API_TARGET || DEFAULT_API_TARGET
  return String(configured).replace(/\/$/, '')
}

export const resolveServerAssetUrl = (value?: string | null): string => {
  if (!value) return ''
  if (isAbsoluteUrl(value) || value.startsWith('data:') || value.startsWith('blob:')) {
    return value
  }

  const normalized = value.startsWith('/') ? value : `/${value}`
  if (!SERVER_ASSET_PREFIXES.some((prefix) => normalized.startsWith(prefix))) {
    return normalized
  }

  return `${getApiTarget()}${normalized}`
}
