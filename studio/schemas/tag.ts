import { defineField, defineType } from 'sanity'

export default defineType({
  name: 'tag',
  title: '标签',
  type: 'document',
  fields: [
    defineField({
      name: 'title',
      title: '名称',
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
  ],
  preview: {
    select: {
      title: 'title',
    },
  },
})
