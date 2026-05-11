export function serializeArticle(article: any) {
  if (!article) return article;

  return {
    ...article,
    cover_image: article.cover_image ?? article.coverImage ?? null,
    published_at: serializeDate(article.published_at ?? article.publishedAt ?? null),
    created_at: serializeDate(article.created_at ?? article.createdAt ?? null),
    updated_at: serializeDate(article.updated_at ?? article.updatedAt ?? null),
  };
}

export function serializeDate(value: unknown): string | null {
  if (!value) return null;
  if (value instanceof Date) return value.toISOString();
  if (typeof value === 'number') return new Date(value).toISOString();
  if (typeof value === 'string') return value;
  return null;
}
