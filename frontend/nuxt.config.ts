// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2025-01-15',
  devtools: { enabled: true },
  modules: [
    '@nuxt/ui',
    '@nuxtjs/supabase',
    '@nuxtjs/color-mode',
    '@vite-pwa/nuxt'
  ],
  colorMode: {
    preference: 'light', // default to light mode
    fallback: 'light',
    classSuffix: ''
  },
  css: ['~/assets/css/main.css'],
  supabase: {
    redirect: false, // Disable automatic redirects since we support anonymous access
    url: process.env.SUPABASE_URL || process.env.NUXT_PUBLIC_SUPABASE_URL,
    key: process.env.SUPABASE_KEY || process.env.NUXT_PUBLIC_SUPABASE_ANON_KEY
  },
  typescript: {
    strict: true
  },
  runtimeConfig: {
    // Private keys (server-side only)
    // Public keys (exposed to client)
    public: {
      // Normalize API URL - remove trailing slash to prevent double slashes
      apiUrl: (process.env.NUXT_PUBLIC_API_URL || 'http://localhost:8000').replace(/\/+$/, ''),
      supabaseUrl: process.env.NUXT_PUBLIC_SUPABASE_URL,
      supabaseAnonKey: process.env.NUXT_PUBLIC_SUPABASE_ANON_KEY
    }
  }
})
