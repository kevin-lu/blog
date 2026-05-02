import { defineField, defineType } from 'sanity'

export default defineType({
  name: 'article',
  title: '文章',
  type: 'document',
  fields: [
    defineField({
      name: 'title',
      title: '标题',
      type: 'string',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'slug',
      title: '别名',
      type: 'slug',
      options: {
        source: 'title',
        maxLength: 96,
      },
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'excerpt',
      title: '摘要',
      type: 'text',
      rows: 3,
      description: '文章摘要，不填写则自动提取正文前150字',
    }),
    defineField({
      name: 'content',
      title: '正文内容',
      type: 'array',
      of: [
        { type: 'block' },
        {
          type: 'image',
          options: {
            hotspot: true,
          },
          fields: [
            {
              name: 'caption',
              type: 'string',
              title: '图片说明',
            },
            {
              name: 'alt',
              type: 'string',
              title: '替代文本',
            },
          ],
        },
        {
          type: 'code',
          title: '代码块',
        },
      ],
    }),
    defineField({
      name: 'coverImage',
      title: '封面图',
      type: 'image',
      options: {
        hotspot: true,
      },
    }),
    defineField({
      name: 'category',
      title: '分类',
      type: 'reference',
      to: [{ type: 'category' }],
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'tags',
      title: '标签',
      type: 'array',
      of: [{ type: 'reference', to: [{ type: 'tag' }] }],
    }),
    defineField({
      name: 'publishedAt',
      title: '发布时间',
      type: 'datetime',
      initialValue: () => new Date().toISOString(),
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'updatedAt',
      title: '更新时间',
      type: 'datetime',
    }),
    defineField({
      name: 'featured',
      title: '精选文章',
      type: 'boolean',
      initialValue: false,
      description: '标记为精选文章将在首页优先展示',
    }),
    defineField({
      name: 'series',
      title: '所属系列',
      type: 'reference',
      to: [{ type: 'series' }],
      description: '如果文章属于某个系列，请选择',
    }),
  ],
  preview: {
    select: {
      title: 'title',
      category: 'category.title',
      media: 'coverImage',
    },
    prepare({ title, category, media }) {
      return {
        title,
        subtitle: category ? `分类: ${category}` : '',
        media,
      }
    },
  },
  orderings: [
    {
      title: '发布时间, 最新',
      name: 'publishedAtDesc',
      by: [{ field: 'publishedAt', direction: 'desc' }],
    },
  ],
})
