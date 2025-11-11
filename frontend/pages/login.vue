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

            <UFormField 
              v-if="isDemoAccount" 
              label="Password" 
              name="password" 
              required
            >
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
              :disabled="!form.email || (isDemoAccount && !form.password)"
            >
              {{ isDemoAccount ? 'Sign In' : 'Send Magic Link' }}
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
const { signInWithMagicLink, signInWithPassword, user, getUserRole } = useAuth()
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

// Check if this is a demo account (ends with @gauntlet.com)
const isDemoAccount = computed(() => {
  return form.email.toLowerCase().endsWith('@gauntlet.com')
})

const handleLogin = async () => {
  if (!form.email) {
    error.value = 'Please enter your email'
    return
  }

  if (isDemoAccount.value && !form.password) {
    error.value = 'Please enter your password'
    return
  }

  loading.value = true
  error.value = null
  successMessage.value = null

  try {
    if (isDemoAccount.value) {
      // Demo accounts use password login
      await signInWithPassword(form.email, form.password)
      // Redirect after successful login
      const role = await getUserRole()
      if (role === 'parent') {
        router.push('/parent/dashboard')
      } else if (role === 'student') {
        router.push('/student/dashboard')
      } else if (role === 'teacher') {
        router.push('/dashboard')
      }
    } else {
      // Regular accounts use magic link
      await signInWithMagicLink(form.email)
      successMessage.value = 'Check your email for the magic link! Click the link to sign in.'
    }
  } catch (err: any) {
    error.value = err.message || (isDemoAccount.value 
      ? 'Failed to sign in. Please check your email and password.' 
      : 'Failed to send magic link. Please try again.')
  } finally {
    loading.value = false
  }
}

useHead({
  title: 'Login - Palabam'
})
</script>

