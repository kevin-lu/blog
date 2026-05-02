export default defineNuxtConfig({
  devtools: { enabled: true },
  modules: ['@nuxt/ui', '@nuxtjs/sanity'],
  css: ['~/assets/css/main.css'],
  sanity: {
    projectId: process.env.NUXT_PUBLIC_SANITY_PROJECT_ID,
    dataset: process.env.NUXT_PUBLIC_SANITY_DATASET || 'production',
    apiVersion: process.env.NUXT_PUBLIC_SANITY_API_VERSION || '2024-05-01',
    useCdn: true,
  },
  runtimeConfig: {
    sanityApiToken: process.env.SANITY_API_READ_TOKEN,
    public: {
      giscusRepo: process.env.NUXT_PUBLIC_GISCUS_REPO,
      giscusRepoId: process.env.NUXT_PUBLIC_GISCUS_REPO_ID,
      giscusCategory: process.env.NUXT_PUBLIC_GISCUS_CATEGORY,
      giscusCategoryId: process.env.NUXT_PUBLIC_GISCUS_CATEGORY_ID,
    }
  },
  app: {
    head: {
      charset: 'utf-8',
      viewport: 'width=device-width, initial-scale=1',
      htmlAttrs: {
        lang: 'zh-CN'
      }
    }
  }
})
