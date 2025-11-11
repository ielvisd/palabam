/**
 * Middleware to require parent role
 * Redirects non-parents to appropriate dashboard
 */
export default defineNuxtRouteMiddleware(async (to) => {
  const { user, getUserRole, isParent } = useAuth()

  // First check authentication
  if (!user.value) {
    return navigateTo({
      path: '/login',
      query: { redirect: to.fullPath }
    })
  }

  // Check if user is a parent
  const role = await getUserRole()
  const parent = await isParent()

  if (role !== 'parent' || !parent) {
    // Redirect based on actual role
    switch (role) {
      case 'student':
        return navigateTo('/student/dashboard')
      case 'teacher':
        return navigateTo('/dashboard')
      default:
        return navigateTo('/')
    }
  }
})

