/**
 * Middleware to require authentication
 * Redirects unauthenticated users to login
 */
export default defineNuxtRouteMiddleware(async (to) => {
  const { user, getUserRole } = useAuth()

  // Check if user is authenticated
  if (!user.value) {
    return navigateTo({
      path: '/login',
      query: { redirect: to.fullPath }
    })
  }

  // Verify user has a role in the database
  const role = await getUserRole()
  if (!role) {
    // User exists in auth but not in database - might be in signup process
    // Allow them to continue (auth callback will handle record creation)
    return
  }
})

