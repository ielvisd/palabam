// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2025-01-15',
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
  },
  runtimeConfig: {
    // Private keys (server-side only)
    // Public keys (exposed to client)
    public: {
      apiUrl: process.env.NUXT_PUBLIC_API_URL || 'http://localhost:8000',
      supabaseUrl: process.env.NUXT_PUBLIC_SUPABASE_URL,
      supabaseAnonKey: process.env.NUXT_PUBLIC_SUPABASE_ANON_KEY
    }
  }
})
