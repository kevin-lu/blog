import type { ArticleListItem, ArticleDetail, Category, Tag, SiteSettings } from '~/types'
import { mockArticles, mockCategories, mockTags, mockSiteSettings } from '~/utils/mockData'

const USE_MOCK_DATA = true

export function useBlogData() {
  const sanity = useNuxtApp().$sanity

  async function fetchArticles(limit: number = 10, start: number = 0): Promise<ArticleListItem[]> {
    if (USE_MOCK_DATA) {
      return mockArticles.slice(start, start + limit) as ArticleListItem[]
    }
    const query = `*[_type == "article" && publishedAt <= now()] | order(publishedAt desc) [${start}...${start + limit}] {
      _id,
      title,
      slug,
      excerpt,
      publishedAt,
      category->{_id, title, slug},
      tags[]->{_id, title, slug},
      featured,
      readingTime,
      order
    }`
    return await sanity.fetch(query)
  }

  async function fetchArticleBySlug(slug: string): Promise<ArticleDetail | null> {
    console.log('Fetching article by slug:', slug)
    if (USE_MOCK_DATA) {
      const article = mockArticles.find(a => a.slug.current === slug)
      console.log('Found article:', article)
      return article as ArticleDetail
    }
    const query = `*[_type == "article" && slug.current == "${slug}"][0] {
      _id,
      title,
      slug,
      excerpt,
      content,
      coverImage,
      publishedAt,
      updatedAt,
      category->{_id, title, slug},
      tags[]->{_id, title, slug},
      featured,
      series->{_id, title, slug},
      readingTime
    }`
    return await sanity.fetch(query)
  }

  async function fetchCategories(): Promise<Category[]> {
    if (USE_MOCK_DATA) {
      return mockCategories as Category[]
    }
    const query = `*[_type == "category"] | order(title asc) {
      _id,
      title,
      slug,
      description,
      "articleCount": count(*[_type == "article" && references(^._id)])
    }`
    return await sanity.fetch(query)
  }

  async function fetchTags(): Promise<Tag[]> {
    if (USE_MOCK_DATA) {
      return mockTags as Tag[]
    }
    const query = `*[_type == "tag"] | order(title asc) {
      _id,
      title,
      slug
    }`
    return await sanity.fetch(query)
  }

  async function fetchSiteSettings(): Promise<SiteSettings | null> {
    if (USE_MOCK_DATA) {
      return mockSiteSettings as SiteSettings
    }
    const query = `*[_type == "siteSettings"][0] {
      title,
      bio,
      description,
      logo,
      social
    }`
    return await sanity.fetch(query)
  }

  async function fetchArticlesByCategory(categorySlug: string, limit: number = 10): Promise<ArticleListItem[]> {
    if (USE_MOCK_DATA) {
      return mockArticles
        .filter(a => a.category.slug.current === categorySlug)
        .slice(0, limit) as ArticleListItem[]
    }
    const query = `*[_type == "article" && category->slug.current == "${categorySlug}" && publishedAt <= now()] | order(publishedAt desc) [0...${limit}] {
      _id,
      title,
      slug,
      excerpt,
      publishedAt,
      category->{_id, title, slug},
      tags[]->{_id, title, slug},
      featured,
      readingTime,
      order
    }`
    return await sanity.fetch(query)
  }

  async function fetchArticlesByTag(tagSlug: string, limit: number = 10): Promise<ArticleListItem[]> {
    if (USE_MOCK_DATA) {
      return mockArticles
        .filter(a => a.tags?.some(t => t.slug.current === tagSlug))
        .slice(0, limit) as ArticleListItem[]
    }
    const query = `*[_type == "article" && "${tagSlug}" in tags[]->slug.current && publishedAt <= now()] | order(publishedAt desc) [0...${limit}] {
      _id,
      title,
      slug,
      excerpt,
      publishedAt,
      category->{_id, title, slug},
      tags[]->{_id, title, slug},
      featured,
      readingTime,
      order
    }`
    return await sanity.fetch(query)
  }

  async function fetchRelatedArticles(articleId: string, categorySlug?: string, tags?: string[], limit: number = 3): Promise<ArticleListItem[]> {
    if (USE_MOCK_DATA) {
      return mockArticles
        .filter(a => a._id !== articleId && a.category.slug.current === categorySlug)
        .slice(0, limit) as ArticleListItem[]
    }
    const tagConditions = tags?.length ? `|| "${tags[0]}" in tags[]->slug.current` : ''
    const query = `*[_type == "article" && _id != "${articleId}" && (category->slug.current == "${categorySlug}" ${tagConditions}) && publishedAt <= now()] | order(publishedAt desc) [0...${limit}] {
      _id,
      title,
      slug,
      excerpt,
      publishedAt,
      category->{_id, title, slug},
      tags[]->{_id, title, slug},
      featured,
      readingTime,
      order
    }`
    return await sanity.fetch(query)
  }

  async function fetchSeriesArticles(seriesSlug: string, excludeId?: string, limit: number = 10): Promise<ArticleListItem[]> {
    if (USE_MOCK_DATA) {
      return mockArticles
        .filter(a => a.series?.slug.current === seriesSlug && a._id !== excludeId)
        .slice(0, limit) as ArticleListItem[]
    }
    const excludeCondition = excludeId ? `&& _id != "${excludeId}"` : ''
    const query = `*[_type == "article" && series->slug.current == "${seriesSlug}" ${excludeCondition} && publishedAt <= now()] | order(publishedAt asc) [0...${limit}] {
      _id,
      title,
      slug,
      excerpt,
      publishedAt,
      category->{_id, title, slug},
      tags[]->{_id, title, slug},
      featured,
      readingTime,
      order
    }`
    return await sanity.fetch(query)
  }

  return {
    fetchArticles,
    fetchArticleBySlug,
    fetchCategories,
    fetchTags,
    fetchSiteSettings,
    fetchArticlesByCategory,
    fetchArticlesByTag,
    fetchRelatedArticles,
    fetchSeriesArticles
  }
}
