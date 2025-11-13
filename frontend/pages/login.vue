<template>
  <UContainer>
    <div class="min-h-screen flex items-center justify-center py-12">
      <div class="w-full max-w-md">
        <UCard>
          <template #header>
            <div class="text-center">
              <h1 class="text-3xl font-bold mb-2 dark:text-white">Welcome Back</h1>
              <p class="text-gray-600 dark:text-gray-400">Sign in to your account</p>
            </div>
          </template>

          <UAlert
            v-if="error"
            color="error"
            variant="soft"
            :title="error"
            class="mb-4"
            @close="error = null"
          />

          <UAlert
            v-if="successMessage"
            color="success"
            variant="soft"
            :title="successMessage"
            class="mb-4"
          />

          <UForm :state="form" class="space-y-4" @submit="handleLogin">
            <UFormField label="Email" name="email" required>
              <UInput
                v-model="form.email"
                type="email"
                placeholder="Enter your email"
                icon="i-heroicons-envelope"
                :disabled="loading"
                autocomplete="email"
              />
            </UFormField>

            <UFormField label="Password" name="password" required>
              <UInput
                v-model="form.password"
                type="password"
                placeholder="Enter your password"
                icon="i-heroicons-lock-closed"
                :disabled="loading"
                autocomplete="current-password"
              />
            </UFormField>

            <UButton
              type="submit"
              block
              size="lg"
              :loading="loading"
              :disabled="!form.email || !form.password"
            >
              Sign In
            </UButton>
          </UForm>

          <div class="mt-6 text-center">
            <p class="text-sm text-gray-600 dark:text-gray-400">
              Don't have an account?
              <NuxtLink to="/signup" class="text-primary hover:underline font-medium">
                Sign up
              </NuxtLink>
            </p>
          </div>

          <div class="mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
            <p class="text-xs text-center text-gray-500 dark:text-gray-400 mb-4">
              Try demo accounts
            </p>
            <div class="space-y-2">
              <UButton
                block
                variant="outline"
                color="neutral"
                :loading="demoLoading === 'teacher'"
                :disabled="loading || demoLoading !== null"
                @click="handleDemoLogin('teacher@gauntlet.com', 'demo123456', 'teacher')"
              >
                <UIcon name="i-heroicons-academic-cap" class="mr-2" />
                Demo Teacher
              </UButton>
              <UButton
                block
                variant="outline"
                color="neutral"
                :loading="demoLoading === 'student'"
                :disabled="loading || demoLoading !== null"
                @click="handleDemoLogin('student@gauntlet.com', 'demo123456', 'student')"
              >
                <UIcon name="i-heroicons-user" class="mr-2" />
                Demo Student
              </UButton>
            </div>
          </div>
        </UCard>
      </div>
    </div>
  </UContainer>
</template>

<script setup lang="ts">
const { signInWithPassword, user, getUserRole, getTeacherId } = useAuth()
const router = useRouter()

// Redirect if already authenticated
onMounted(async () => {
  if (user.value) {
    const role = await getUserRole()
    if (role === 'parent') {
      router.push('/parent/dashboard')
    } else if (role === 'student') {
      router.push('/student/dashboard')
    } else if (role === 'teacher') {
      router.push('/dashboard')
    }
  }
})

const form = reactive({
  email: '',
  password: ''
})

const loading = ref(false)
const demoLoading = ref<'teacher' | 'student' | null>(null)
const error = ref<string | null>(null)
const successMessage = ref<string | null>(null)

const handleLogin = async () => {
  if (!form.email || !form.password) {
    error.value = 'Please enter your email and password'
    return
  }

  loading.value = true
  error.value = null
  successMessage.value = null

  try {
    await signInWithPassword(form.email, form.password)
    
    // Wait for session to be established
    await nextTick()
    
    // Wait a bit for the reactive user to update
    let attempts = 0
    let role: 'student' | 'teacher' | 'admin' | 'parent' | null = null
    while (attempts < 10 && !role) {
      await new Promise(resolve => setTimeout(resolve, 100))
      role = await getUserRole()
      attempts++
    }
    
    // If role is still null, try to detect teacher by checking if teacher record exists
    if (!role) {
      const teacherId = await getTeacherId()
      if (teacherId) {
        role = 'teacher'
      }
    }
    
    // Redirect based on role
    if (role === 'parent') {
      router.push('/parent/dashboard')
    } else if (role === 'student') {
      router.push('/student/dashboard')
    } else if (role === 'teacher') {
      router.push('/dashboard')
    } else {
      // If no role yet, redirect to home (which will show appropriate UI)
      router.push('/')
    }
  } catch (err: any) {
    error.value = err.message || 'Failed to sign in. Please check your email and password.'
    console.error('Login error:', err)
  } finally {
    loading.value = false
  }
}

const handleDemoLogin = async (email: string, password: string, accountType: 'teacher' | 'student') => {
  demoLoading.value = accountType
  error.value = null
  successMessage.value = null

  try {
    await signInWithPassword(email, password)
    
    // Wait for session to be established
    await nextTick()
    
    // Wait a bit for the reactive user to update
    let attempts = 0
    let role: 'student' | 'teacher' | 'admin' | 'parent' | null = null
    while (attempts < 10 && !role) {
      await new Promise(resolve => setTimeout(resolve, 100))
      role = await getUserRole()
      attempts++
    }
    
    // If role is still null, try to detect teacher by checking if teacher record exists
    if (!role) {
      const teacherId = await getTeacherId()
      if (teacherId) {
        role = 'teacher'
      }
    }
    
    // Redirect based on role
    if (role === 'parent') {
      router.push('/parent/dashboard')
    } else if (role === 'student') {
      router.push('/student/dashboard')
    } else if (role === 'teacher') {
      router.push('/dashboard')
    } else {
      // If no role yet, redirect to home (which will show appropriate UI)
      router.push('/')
    }
  } catch (err: any) {
    error.value = err.message || 'Failed to sign in with demo account. Please try again.'
    console.error('Demo login error:', err)
  } finally {
    demoLoading.value = null
  }
}

useHead({
  title: 'Login - Palabam'
})
</script>

