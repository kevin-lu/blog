import { defineField, defineType } from 'sanity'

export default defineType({
  name: 'siteSettings',
  title: '站点设置',
  type: 'document',
  fields: [
    defineField({
      name: 'title',
      title: '网站标题',
      type: 'string',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'description',
      title: '网站描述',
      type: 'text',
      rows: 2,
      description: '用于 SEO 和社交媒体分享',
    }),
    defineField({
      name: 'author',
      title: '作者名称',
      type: 'string',
    }),
    defineField({
      name: 'avatar',
      title: '头像',
      type: 'image',
      options: {
        hotspot: true,
      },
    }),
    defineField({
      name: 'bio',
      title: '个人简介',
      type: 'text',
      rows: 3,
    }),
    defineField({
      name: 'socialLinks',
      title: '社交链接',
      type: 'array',
      of: [
        {
          type: 'object',
          fields: [
            defineField({
              name: 'platform',
              title: '平台',
              type: 'string',
              options: {
                list: [
                  { title: 'GitHub', value: 'github' },
                  { title: 'Twitter / X', value: 'twitter' },
                  { title: '微博', value: 'weibo' },
                  { title: '知乎', value: 'zhihu' },
                  { title: '掘金', value: 'juejin' },
                  { title: '邮箱', value: 'email' },
                  { title: '其他', value: 'other' },
                ],
              },
            }),
            defineField({
              name: 'url',
              title: '链接',
              type: 'url',
            }),
          ],
        },
      ],
    }),
  ],
  preview: {
    select: {
      title: 'title',
    },
  },
})
