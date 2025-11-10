// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2024-04-03',
  devtools: { enabled: true },
  modules: [
    '@nuxt/ui',
    '@nuxtjs/tailwindcss',
    '@nuxtjs/supabase',
    '@vite-pwa/nuxt'
  ],
  css: ['~/assets/css/tailwind.css'],
  supabase: {
    redirectOptions: {
      login: '/login',
      callback: '/confirm'
    }
  },
  typescript: {
    strict: true
  }
})

