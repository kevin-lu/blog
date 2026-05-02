import type { ArticleListItem, ArticleDetail, Category, Tag, SiteSettings } from '~/types'
import { 
  getArticlesQuery, 
  getArticleBySlugQuery, 
  getCategoriesQuery, 
  getTagsQuery,
  getSiteSettingsQuery 
} from '~/utils/helpers'

export function useSanity() {
  const sanity = useNuxtApp().$sanity

  /**
   * 获取文章列表
   */
  async function fetchArticles(limit: number = 10, start: number = 0): Promise<ArticleListItem[]> {
    const query = getArticlesQuery(limit, start)
    return await sanity.fetch(query)
  }

  /**
   * 获取单篇文章
   */
  async function fetchArticleBySlug(slug: string): Promise<ArticleDetail | null> {
    const query = getArticleBySlugQuery(slug)
    return await sanity.fetch(query)
  }

  /**
   * 获取分类列表
   */
  async function fetchCategories(): Promise<Category[]> {
    const query = getCategoriesQuery()
    return await sanity.fetch(query)
  }

  /**
   * 获取标签列表
   */
  async function fetchTags(): Promise<Tag[]> {
    const query = getTagsQuery()
    return await sanity.fetch(query)
  }

  /**
   * 获取站点设置
   */
  async function fetchSiteSettings(): Promise<SiteSettings | null> {
    const query = getSiteSettingsQuery()
    return await sanity.fetch(query)
  }

  /**
   * 获取分类下的文章
   */
  async function fetchArticlesByCategory(categorySlug: string, limit: number = 10): Promise<ArticleListItem[]> {
    const query = `*[_type == "article" && category->slug.current == "${categorySlug}" && publishedAt <= now()] | order(publishedAt desc) [0...${limit}] {
      _id,
      title,
      slug,
      excerpt,
      coverImage,
      "category": category->title,
      "categorySlug": category->slug.current,
      "tags": tags[]->title,
      publishedAt,
      "readingTime": round(length(pt::text(content)) / 200)
    }`
    return await sanity.fetch(query)
  }

  /**
   * 获取标签下的文章
   */
  async function fetchArticlesByTag(tagSlug: string, limit: number = 10): Promise<ArticleListItem[]> {
    const query = `*[_type == "article" && "${tagSlug}" in tags[]->slug.current && publishedAt <= now()] | order(publishedAt desc) [0...${limit}] {
      _id,
      title,
      slug,
      excerpt,
      coverImage,
      "category": category->title,
      "categorySlug": category->slug.current,
      "tags": tags[]->title,
      publishedAt,
      "readingTime": round(length(pt::text(content)) / 200)
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
  }
}
