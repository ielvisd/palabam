<template>
  <UContainer>
    <div class="min-h-screen flex items-center justify-center">
      <div class="text-center">
        <div v-if="loading" class="space-y-4">
          <UIcon name="i-heroicons-arrow-path" class="w-12 h-12 animate-spin mx-auto text-primary" />
          <p class="text-lg">Verifying your email...</p>
        </div>
        <div v-else-if="error" class="space-y-4">
          <UIcon name="i-heroicons-exclamation-triangle" class="w-12 h-12 mx-auto text-error" />
          <p class="text-lg text-error">{{ error }}</p>
          <UButton to="/login" color="primary">Go to Login</UButton>
        </div>
        <div v-else class="space-y-4">
          <UIcon name="i-heroicons-check-circle" class="w-12 h-12 mx-auto text-success" />
          <p class="text-lg">Email verified! Redirecting...</p>
        </div>
      </div>
    </div>
  </UContainer>
</template>

<script setup lang="ts">
const supabase = useSupabaseClient()
const router = useRouter()
const route = useRoute()
const { createStudentRecord, createStudentRecordWithInvite, createParentRecord, createTeacherRecord, linkStudentToParent } = useAuth()

const loading = ref(true)
const error = ref<string | null>(null)

onMounted(async () => {
  try {
    // Handle the auth callback
    const { data, error: authError } = await supabase.auth.getSession()
    
    if (authError) {
      throw authError
    }

    if (!data.session?.user) {
      throw new Error('No user session found')
    }

    const user = data.session.user
    const userMetadata = user.user_metadata || {}
    const role = userMetadata.role || 'student'
    const name = userMetadata.name || user.email?.split('@')[0] || 'User'
    const email = user.email || ''
    const inviteCode = userMetadata.invite_code || route.query.invite as string || null

    // Check if user record already exists
    const { data: existingUser } = await supabase
      .from('users')
      .select('id')
      .eq('id', user.id)
      .single()

    if (!existingUser) {
      // Create user record based on role
      if (role === 'student') {
        // If signing up via invite, use the invite flow
        if (inviteCode) {
          await createStudentRecordWithInvite(user.id, email, name, inviteCode)
        } else {
          await createStudentRecord(user.id, email, name)
          
          // Check for parent email in signup data
          const signupDataStr = sessionStorage.getItem('signup_data')
          if (signupDataStr) {
            try {
              const signupData = JSON.parse(signupDataStr)
              if (signupData.parentEmail) {
                // Try to link to parent (parent might not be signed up yet, that's ok)
                try {
                  await linkStudentToParent(signupData.parentEmail)
                } catch (err) {
                  console.warn('Could not link to parent:', err)
                  // Not a critical error, parent can link later
                }
              }
              sessionStorage.removeItem('signup_data')
            } catch (err) {
              console.warn('Error processing signup data:', err)
            }
          }
        }
      } else if (role === 'parent') {
        await createParentRecord(user.id, email, name)
        
        // Check for children in signup data
        const signupDataStr = sessionStorage.getItem('signup_data')
        if (signupDataStr) {
          try {
            const signupData = JSON.parse(signupDataStr)
            if (signupData.children && signupData.children.length > 0) {
              // Children will need to sign up separately and link via email
              // We can't create student accounts here as they need their own auth
              console.log('Children to link:', signupData.children)
            }
            sessionStorage.removeItem('signup_data')
          } catch (err) {
            console.warn('Error processing signup data:', err)
          }
        }
      } else if (role === 'teacher') {
        await createTeacherRecord(user.id, email, name)
      }
    }

    // Redirect based on role
    await router.push(getRedirectPath(role))
  } catch (err: any) {
    console.error('Auth callback error:', err)
    error.value = err.message || 'Failed to verify email. Please try again.'
  } finally {
    loading.value = false
  }
})

const getRedirectPath = (role: string): string => {
  switch (role) {
    case 'parent':
      return '/parent/dashboard'
    case 'student':
      return '/student/dashboard'
    case 'teacher':
      return '/dashboard'
    default:
      return '/'
  }
}

useHead({
  title: 'Verifying Email - Palabam'
})
</script>

