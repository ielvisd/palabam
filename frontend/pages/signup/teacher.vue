<template>
  <UContainer>
    <div class="min-h-screen flex items-center justify-center py-12">
      <div class="w-full max-w-md">
        <UCard>
          <template #header>
            <div class="text-center">
              <h1 class="text-3xl font-bold mb-2 dark:text-white">Teacher Sign Up</h1>
              <p class="text-gray-600 dark:text-gray-400">Create your teacher account</p>
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

          <UForm :state="form" class="space-y-4" @submit="handleSignup">
            <UFormField label="Name" name="name" required>
              <UInput
                v-model="form.name"
                placeholder="Your full name"
                icon="i-heroicons-user"
                :disabled="loading"
              />
            </UFormField>

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
                placeholder="Create a password (min 8 characters)"
                icon="i-heroicons-lock-closed"
                :disabled="loading"
                autocomplete="new-password"
              />
            </UFormField>

            <UButton
              type="submit"
              block
              size="lg"
              :loading="loading"
              :disabled="!form.email || !form.name || !form.password || form.password.length < 8"
            >
              Create Account
            </UButton>
          </UForm>

          <div class="mt-6 text-center">
            <p class="text-sm text-gray-600 dark:text-gray-400">
              Already have an account?
              <NuxtLink to="/login" class="text-primary hover:underline font-medium">
                Sign in
              </NuxtLink>
            </p>
          </div>
        </UCard>
      </div>
    </div>
  </UContainer>
</template>

<script setup lang="ts">
const { signUpTeacher } = useAuth()
const router = useRouter()

const form = reactive({
  name: '',
  email: '',
  password: ''
})

const loading = ref(false)
const error = ref<string | null>(null)
const successMessage = ref<string | null>(null)

const handleSignup = async () => {
  if (!form.email || !form.name || !form.password) {
    error.value = 'Please fill in all required fields'
    return
  }

  if (form.password.length < 8) {
    error.value = 'Password must be at least 8 characters'
    return
  }

  loading.value = true
  error.value = null
  successMessage.value = null

  try {
    await signUpTeacher(form.email, form.password, form.name)
    successMessage.value = 'Account created successfully! Redirecting...'
    
    // Redirect to teacher dashboard after a short delay
    setTimeout(() => {
      window.location.href = '/dashboard'
    }, 1500)
  } catch (err: any) {
    error.value = err.message || 'Failed to create account. Please try again.'
  } finally {
    loading.value = false
  }
}

useHead({
  title: 'Teacher Sign Up - Palabam'
})
</script>

