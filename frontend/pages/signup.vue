<template>
  <UContainer>
    <div class="min-h-screen flex items-center justify-center py-12">
      <div class="w-full max-w-md">
        <UCard>
          <template #header>
            <div class="text-center">
              <h1 class="text-3xl font-bold mb-2 dark:text-white">Create Account</h1>
              <p class="text-gray-600 dark:text-gray-400">Choose your account type</p>
            </div>
          </template>

          <div class="space-y-4">
            <UButton
              to="/signup/parent"
              block
              size="xl"
              color="primary"
              variant="outline"
              class="h-auto py-6"
            >
              <div class="text-left w-full">
                <div class="font-semibold text-lg mb-1">Parent</div>
                <div class="text-sm text-gray-600 dark:text-gray-400">
                  Track your child's progress and view their achievements
                </div>
              </div>
            </UButton>

            <UButton
              block
              size="xl"
              color="primary"
              variant="outline"
              class="h-auto py-6"
              @click="navigateTo('/signup/teacher')"
            >
              <div class="text-left w-full">
                <div class="font-semibold text-lg mb-1">Teacher</div>
                <div class="text-sm text-gray-600 dark:text-gray-400">
                  Create classes, invite students, and track progress
                </div>
              </div>
            </UButton>
          </div>
          
          <UAlert
            color="info"
            variant="soft"
            title="Student Signup"
            description="Students must sign up via an invite link from their teacher. Please contact your teacher for an invite link."
            class="mt-4"
          />

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
const { user, getUserRole } = useAuth()
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

useHead({
  title: 'Sign Up - Palabam'
})
</script>

