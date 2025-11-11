/**
 * Global middleware - authentication is now required
 * Individual routes use specific middleware (auth, parent, student)
 * This file is kept for backwards compatibility but does nothing
 */
export default defineNuxtRouteMiddleware((to) => {
  // Authentication is now required for all student activities
  // Use auth.ts, parent.ts, or student.ts middleware on specific routes
})

