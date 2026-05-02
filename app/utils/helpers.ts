import type { Article } from '~/types'

/**
 * 格式化日期
 */
export function formatDate(dateString: string): string {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
}

/**
 * 计算阅读时间（分钟）
 */
export function calculateReadingTime(content?: any[]): number {
  if (!content || !Array.isArray(content)) return 1
  
  // 提取所有文本内容
  const text = content
    .map((block) => {
      if (block._type === 'block' && block.children) {
        return block.children.map((child: any) => child.text || '').join('')
      }
      return ''
    })
    .join('')
  
  // 假设平均阅读速度为每分钟 200 字
  const wordsPerMinute = 200
  const wordCount = text.length
  const readingTime = Math.ceil(wordCount / wordsPerMinute)
  
  return Math.max(1, readingTime)
}

/**
 * 生成摘要（从正文提取前 n 个字符）
 */
export function generateExcerpt(content?: any[], maxLength: number = 150): string {
  if (!content || !Array.isArray(content)) return ''
  
  const text = content
    .map((block) => {
      if (block._type === 'block' && block.children) {
        return block.children.map((child: any) => child.text || '').join('')
      }
      return ''
    })
    .join('')
    .replace(/\s+/g, ' ')
    .trim()
  
  if (text.length <= maxLength) return text
  return text.slice(0, maxLength) + '...'
}

/**
 * 获取文章列表的 GROQ 查询
 */
export function getArticlesQuery(limit: number = 10, start: number = 0): string {
  return `*[_type == "article" && publishedAt <= now()] | order(publishedAt desc) [${start}...${start + limit}] {
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
}

/**
 * 获取单篇文章的 GROQ 查询
 */
export function getArticleBySlugQuery(slug: string): string {
  return `*[_type == "article" && slug.current == "${slug}"][0] {
    _id,
    title,
    slug,
    excerpt,
    content,
    coverImage,
    "category": category->{ _id, title, slug },
    "tags": tags[]->{ _id, title, slug },
    publishedAt,
    updatedAt,
    "readingTime": round(length(pt::text(content)) / 200),
    "series": series->{ _id, title, slug },
    "seriesArticles": *[_type == "article" && series._ref == ^.series._ref] | order(publishedAt asc) {
      title, slug
    }
  }`
}

/**
 * 获取分类列表的 GROQ 查询
 */
export function getCategoriesQuery(): string {
  return `*[_type == "category"] | order(title asc) {
    _id,
    title,
    slug,
    description,
    "articleCount": count(*[_type == "article" && references(^._id)])
  }`
}

/**
 * 获取标签列表的 GROQ 查询
 */
export function getTagsQuery(): string {
  return `*[_type == "tag"] | order(title asc) {
    _id,
    title,
    slug,
    "articleCount": count(*[_type == "article" && references(^._id)])
  }`
}

/**
 * 获取站点设置的 GROQ 查询
 */
export function getSiteSettingsQuery(): string {
  return `*[_type == "siteSettings"][0]`
}
