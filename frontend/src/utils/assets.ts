const DEFAULT_API_TARGET = 'http://127.0.0.1:5001'

const SERVER_ASSET_PREFIXES = ['/uploads/', '/images/', '/documents/']

const isAbsoluteUrl = (value: string) => /^(?:[a-z]+:)?\/\//i.test(value)

const extractAssetPath = (value: unknown): string => {
  if (!value) return ''

  if (typeof value === 'string') {
    const trimmed = value.trim()
    if (!trimmed) return ''

    if ((trimmed.startsWith('{') && trimmed.endsWith('}')) || (trimmed.startsWith('[') && trimmed.endsWith(']'))) {
      try {
        return extractAssetPath(JSON.parse(trimmed))
      } catch {
        return trimmed
      }
    }

    return trimmed
  }

  if (typeof value === 'object') {
    const maybeUrl = (value as { url?: unknown }).url
    if (typeof maybeUrl === 'string') {
      return maybeUrl.trim()
    }
  }

  return ''
}

const getApiTarget = () => {
  const configured = (import.meta as any).env.VITE_API_TARGET || DEFAULT_API_TARGET
  return String(configured).replace(/\/$/, '')
}

export const resolveServerAssetUrl = (value?: unknown): string => {
  const rawValue = extractAssetPath(value)
  if (!rawValue) return ''
  if (isAbsoluteUrl(rawValue) || rawValue.startsWith('data:') || rawValue.startsWith('blob:')) {
    return rawValue
  }

  let normalized = rawValue.startsWith('/') ? rawValue : `/${rawValue}`
  if (normalized.startsWith('/images/')) {
    normalized = `/uploads${normalized}`
  } else if (normalized.startsWith('/documents/')) {
    normalized = `/uploads${normalized}`
  }

  if (!SERVER_ASSET_PREFIXES.some((prefix) => normalized.startsWith(prefix))) {
    return normalized
  }

  return `${getApiTarget()}${normalized}`
}
