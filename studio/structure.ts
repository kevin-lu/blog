import type { StructureResolver } from 'sanity/structure'

export const structure: StructureResolver = (S) =>
  S.list()
    .title('内容管理')
    .items([
      S.listItem()
        .title('站点设置')
        .child(
          S.editor()
            .schemaType('siteSettings')
            .documentId('siteSettings')
        ),
      S.divider(),
      S.documentTypeListItem('article').title('文章'),
      S.documentTypeListItem('category').title('分类'),
      S.documentTypeListItem('tag').title('标签'),
      S.documentTypeListItem('series').title('系列'),
    ])
