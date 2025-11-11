/**
 * Middleware to require student role
 * Redirects non-students to appropriate dashboard
 */
export default defineNuxtRouteMiddleware(async (to) => {
  const { user, getUserRole, getStudentId } = useAuth()

  // First check authentication
  if (!user.value) {
    return navigateTo({
      path: '/login',
      query: { redirect: to.fullPath }
    })
  }

  // Check if user is a student
  const role = await getUserRole()
  const studentId = await getStudentId()

  if (role !== 'student' || !studentId) {
    // Redirect based on actual role
    switch (role) {
      case 'parent':
        return navigateTo('/parent/dashboard')
      case 'teacher':
        return navigateTo('/dashboard')
      default:
        return navigateTo('/')
    }
  }
})

