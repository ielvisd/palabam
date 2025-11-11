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
        </UCard>
      </div>
    </div>
  </UContainer>
</template>

<script setup lang="ts">
const { signInWithPassword, user, getUserRole } = useAuth()
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
    
    // Redirect based on role
    if (role === 'parent') {
      router.push('/parent/dashboard')
    } else if (role === 'student') {
      router.push('/student/dashboard')
    } else if (role === 'teacher') {
      router.push('/dashboard')
    } else {
      // If no role yet, redirect to home
      router.push('/')
    }
  } catch (err: any) {
    error.value = err.message || 'Failed to sign in. Please check your email and password.'
    console.error('Login error:', err)
  } finally {
    loading.value = false
  }
}

useHead({
  title: 'Login - Palabam'
})
</script>

