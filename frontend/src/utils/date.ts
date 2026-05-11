export function formatDate(value?: string | Date | null, fallback = ''): string {
  const date = parseDate(value);
  if (!date) return fallback;

  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
}

export function formatDateTime(value?: string | Date | null, fallback = '-'): string {
  const date = parseDate(value);
  if (!date) return fallback;
  return date.toLocaleString('zh-CN');
}

export function getArticleDate(article: {
  published_at?: string | null;
  publishedAt?: string | null;
  created_at?: string | null;
  createdAt?: string | null;
}) {
  return article.published_at || article.publishedAt || article.created_at || article.createdAt || null;
}

function parseDate(value?: string | Date | null): Date | null {
  if (!value) return null;
  const date = value instanceof Date ? value : new Date(value);
  return Number.isNaN(date.getTime()) ? null : date;
}
