<template>
  <UContainer>
    <div class="min-h-screen flex items-center justify-center py-12">
      <div class="w-full max-w-md">
        <UCard>
          <template #header>
            <div class="text-center">
              <h1 class="text-3xl font-bold mb-2 dark:text-white">Student Sign Up</h1>
              <p class="text-gray-600 dark:text-gray-400">Join your class</p>
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

          <div v-if="loadingInvite" class="text-center py-8">
            <p class="text-gray-600 dark:text-gray-400">Validating invite...</p>
          </div>

          <div v-else-if="inviteData && inviteData.valid">
            <UAlert
              color="info"
              variant="soft"
              :title="`Joining ${inviteData.class_name}`"
              :description="`Teacher: ${inviteData.teacher_name}`"
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
          </div>

          <div v-else class="text-center py-8">
            <UAlert
              color="error"
              variant="soft"
              title="Invalid Invite"
              description="This invite link is invalid or has expired. Please contact your teacher for a new invite."
              class="mb-4"
            />
            <UButton
              to="/login"
              variant="outline"
            >
              Back to Login
            </UButton>
          </div>

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
const route = useRoute()
const { signUpStudentViaInvite, validateInviteCode } = useAuth()

const inviteCode = route.params.code as string

const form = reactive({
  name: '',
  email: ''
})

const loading = ref(false)
const loadingInvite = ref(true)
const error = ref<string | null>(null)
const successMessage = ref<string | null>(null)
const inviteData = ref<any>(null)

// Validate invite code on mount
onMounted(async () => {
  try {
    const data = await validateInviteCode(inviteCode)
    inviteData.value = data
  } catch (err: any) {
    console.error('Error validating invite:', err)
    inviteData.value = { valid: false }
  } finally {
    loadingInvite.value = false
  }
})

const handleSignup = async () => {
  if (!form.email || !form.name) {
    error.value = 'Please fill in your name and email'
    return
  }

  loading.value = true
  error.value = null
  successMessage.value = null

  try {
    await signUpStudentViaInvite(inviteCode, form.email, form.name)
    successMessage.value = 'Check your email for the magic link! Click the link to complete your signup and join the class.'
  } catch (err: any) {
    error.value = err.message || 'Failed to create account. Please try again.'
  } finally {
    loading.value = false
  }
}

useHead({
  title: 'Student Sign Up - Palabam'
})
</script>

