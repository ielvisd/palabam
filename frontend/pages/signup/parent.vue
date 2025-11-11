<template>
  <UContainer>
    <div class="min-h-screen flex items-center justify-center py-12">
      <div class="w-full max-w-2xl">
        <UCard>
          <template #header>
            <div class="text-center">
              <h1 class="text-3xl font-bold mb-2 dark:text-white">Parent Sign Up</h1>
              <p class="text-gray-600 dark:text-gray-400">Create your account and link your children</p>
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

            <div class="border-t border-gray-200 dark:border-gray-700 pt-4">
              <h3 class="text-lg font-semibold mb-3 dark:text-white">Link to Existing Student (Optional)</h3>
              <p class="text-sm text-gray-600 dark:text-gray-400 mb-4">
                Link to your child's existing account using their email address. You can add more children after signing up.
              </p>

              <div v-for="(child, index) in form.children" :key="index" class="mb-4 space-y-2">
                <div class="flex gap-2">
                  <UFormField :label="`Student ${index + 1} Email`" class="flex-1">
                    <UInput
                      v-model="child.email"
                      type="email"
                      placeholder="Student's email address"
                      icon="i-heroicons-envelope"
                      :disabled="loading"
                    />
                  </UFormField>
                  <UButton
                    v-if="form.children.length > 1"
                    color="error"
                    variant="ghost"
                    icon="i-heroicons-trash"
                    :disabled="loading"
                    @click="removeChild(index)"
                  />
                </div>
              </div>

              <UButton
                type="button"
                variant="outline"
                size="sm"
                :disabled="loading"
                @click="addChild"
              >
                <UIcon name="i-heroicons-plus" class="mr-1" />
                Add Another Student
              </UButton>
            </div>

            <UButton
              type="submit"
              block
              size="lg"
              :loading="loading"
              :disabled="!form.email || !form.name"
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
const { signUpParent } = useAuth()
const router = useRouter()

const form = reactive({
  name: '',
  email: '',
  children: [{ email: '' }] as Array<{ email: string }>
})

const loading = ref(false)
const error = ref<string | null>(null)
const successMessage = ref<string | null>(null)

const addChild = () => {
  form.children.push({ email: '' })
}

const removeChild = (index: number) => {
  form.children.splice(index, 1)
}

const handleSignup = async () => {
  if (!form.email || !form.name) {
    error.value = 'Please fill in your name and email'
    return
  }

  loading.value = true
  error.value = null
  successMessage.value = null

  try {
    // Store form data in session storage for after email verification
    const signupData = {
      name: form.name,
      email: form.email,
      role: 'parent',
      children: form.children.filter(c => c.email)
    }
    sessionStorage.setItem('signup_data', JSON.stringify(signupData))

    await signUpParent(form.email, form.name)
    successMessage.value = 'Check your email for the magic link! After verifying, you can link your children.'
  } catch (err: any) {
    error.value = err.message || 'Failed to create account. Please try again.'
  } finally {
    loading.value = false
  }
}

useHead({
  title: 'Parent Sign Up - Palabam'
})
</script>

