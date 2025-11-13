<template>
  <UContainer>
    <div class="py-12">
      <div class="text-center mb-12">
        <h1 class="text-5xl font-bold mb-4 dark:text-white">Palabam</h1>
        <p class="text-xl text-gray-600 dark:text-gray-300 mb-2">Personalized Vocabulary Recommendation Engine</p>
        <p class="text-gray-500 dark:text-gray-400">Automate vocabulary gap detection and provide personalized word recommendations for your students</p>
      </div>

      <!-- Feature Cards -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
        <UCard>
          <div class="text-center">
            <UIcon name="i-heroicons-document-text" class="text-4xl text-primary mb-4" />
            <h3 class="text-xl font-semibold mb-2 dark:text-white">Analyze Transcripts</h3>
            <p class="text-gray-600 dark:text-gray-300">
              Upload or paste student conversation transcripts and writing samples for AI-powered analysis
            </p>
          </div>
        </UCard>

        <UCard>
          <div class="text-center">
            <UIcon name="i-heroicons-light-bulb" class="text-4xl text-primary mb-4" />
            <h3 class="text-xl font-semibold mb-2 dark:text-white">Get Recommendations</h3>
            <p class="text-gray-600 dark:text-gray-300">
              Receive 5-7 personalized vocabulary words tailored to each student's proficiency level
            </p>
          </div>
        </UCard>

        <UCard>
          <div class="text-center">
            <UIcon name="i-heroicons-chart-bar" class="text-4xl text-primary mb-4" />
            <h3 class="text-xl font-semibold mb-2 dark:text-white">Track Progress</h3>
            <p class="text-gray-600 dark:text-gray-300">
              View all student recommendations in one dashboard and export for lesson planning
            </p>
          </div>
        </UCard>
      </div>

      <!-- Action Buttons -->
      <div class="space-y-4">
        <div v-if="!user" class="text-center">
          <h2 class="text-2xl font-semibold mb-4 dark:text-white">Get Started</h2>
          <p class="text-gray-600 dark:text-gray-400 mb-6">
            Sign in or create an account to access Palabam
          </p>
          <div class="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <UButton
              to="/login"
              size="xl"
              color="primary"
              class="w-full sm:w-auto"
            >
              <UIcon name="i-heroicons-arrow-right-on-rectangle" class="mr-2" />
              Sign In
            </UButton>
            <UButton
              to="/signup"
              size="xl"
              variant="outline"
              color="neutral"
              class="w-full sm:w-auto"
            >
              <UIcon name="i-heroicons-user-plus" class="mr-2" />
              Sign Up (Parent/Teacher)
            </UButton>
          </div>
          <UAlert
            color="info"
            variant="soft"
            title="Student Signup"
            description="Students must sign up via an invite link from their teacher. Please contact your teacher for an invite link."
            class="mt-6 max-w-2xl mx-auto"
          />
        </div>

        <div v-else class="space-y-6">
          <!-- Parent Actions -->
          <template v-if="userRole === 'parent'">
            <div class="text-center mb-4">
              <h2 class="text-2xl font-semibold mb-2 dark:text-white">Parent Portal</h2>
            </div>
            <div class="flex flex-col sm:flex-row gap-4 justify-center items-center">
              <UButton
                to="/parent/dashboard"
                size="xl"
                color="primary"
                class="w-full sm:w-auto"
              >
                <UIcon name="i-heroicons-squares-2x2" class="mr-2" />
                View Dashboard
              </UButton>
            </div>
          </template>

          <!-- Student Actions -->
          <template v-else-if="userRole === 'student'">
            <div class="text-center mb-4">
              <h2 class="text-2xl font-semibold mb-2 dark:text-white">Student Portal</h2>
            </div>
            <div class="flex flex-col sm:flex-row gap-4 justify-center items-center">
              <UButton
                to="/student/dashboard"
                size="xl"
                color="primary"
                class="w-full sm:w-auto"
              >
                <UIcon name="i-heroicons-chart-bar" class="mr-2" />
                My Progress
              </UButton>
              <UButton
                to="/story-spark"
                size="xl"
                variant="outline"
                color="neutral"
                class="w-full sm:w-auto"
              >
                <UIcon name="i-heroicons-sparkles" class="mr-2" />
                Tell a Story
              </UButton>
            </div>
          </template>

          <!-- Teacher Actions -->
          <template v-else-if="userRole === 'teacher'">
            <div class="text-center mb-4">
              <h2 class="text-2xl font-semibold mb-2 dark:text-white">Educator Portal</h2>
            </div>
            <div class="flex flex-col sm:flex-row gap-4 justify-center items-center">
              <UButton
                to="/dashboard"
                size="xl"
                color="primary"
                class="w-full sm:w-auto"
              >
                <UIcon name="i-heroicons-squares-2x2" class="mr-2" />
                View Dashboard
              </UButton>
            </div>
          </template>
        </div>
      </div>

      <!-- Quick Stats (if available) -->
      <div v-if="stats" class="mt-12 grid grid-cols-1 md:grid-cols-4 gap-4">
        <UCard>
          <div class="text-center">
            <div class="text-3xl font-bold text-primary">{{ stats.totalStudents || 0 }}</div>
            <div class="text-sm text-gray-600 dark:text-gray-300 mt-1">Students</div>
          </div>
        </UCard>
        <UCard>
          <div class="text-center">
            <div class="text-3xl font-bold text-green-600 dark:text-green-400">{{ stats.totalProfiles || 0 }}</div>
            <div class="text-sm text-gray-600 dark:text-gray-300 mt-1">Profiles Analyzed</div>
          </div>
        </UCard>
        <UCard>
          <div class="text-center">
            <div class="text-3xl font-bold text-blue-600 dark:text-blue-400">{{ stats.totalRecommendations || 0 }}</div>
            <div class="text-sm text-gray-600 dark:text-gray-300 mt-1">Words Recommended</div>
          </div>
        </UCard>
        <UCard>
          <div class="text-center">
            <div class="text-3xl font-bold text-purple-600 dark:text-purple-400">{{ stats.avgWordsPerStudent || 0 }}</div>
            <div class="text-sm text-gray-600 dark:text-gray-300 mt-1">Avg Words/Student</div>
          </div>
        </UCard>
      </div>
    </div>
  </UContainer>
</template>

<script setup lang="ts">
const { user, getUserRole, getTeacherId } = useAuth()
const userRole = ref<'parent' | 'student' | 'teacher' | 'admin' | null>(null)

// Fetch user role and redirect if needed
onMounted(async () => {
  if (user.value) {
    // Try to get role with retries (similar to login page)
    let role = await getUserRole()
    let attempts = 0
    
    // If no role, try a few more times (might be creating user record)
    while (!role && attempts < 5) {
      await new Promise(resolve => setTimeout(resolve, 200))
      role = await getUserRole()
      attempts++
    }
    
    // If still no role, try to detect teacher by checking teacher record
    if (!role) {
      const teacherId = await getTeacherId()
      if (teacherId) {
        role = 'teacher'
      }
    }
    
    userRole.value = role
    
    // Auto-redirect authenticated users to their dashboard
    if (role === 'parent') {
      await navigateTo('/parent/dashboard')
    } else if (role === 'student') {
      await navigateTo('/student/dashboard')
    } else if (role === 'teacher') {
      await navigateTo('/dashboard')
    }
  }
})

// Watch for auth changes
watch(user, async (newUser) => {
  if (newUser) {
    // Try to get role with retries (similar to login page)
    let role = await getUserRole()
    let attempts = 0
    
    // If no role, try a few more times (might be creating user record)
    while (!role && attempts < 5) {
      await new Promise(resolve => setTimeout(resolve, 200))
      role = await getUserRole()
      attempts++
    }
    
    // If still no role, try to detect teacher by checking teacher record
    if (!role) {
      const teacherId = await getTeacherId()
      if (teacherId) {
        role = 'teacher'
      }
    }
    
    userRole.value = role
    
    // Auto-redirect authenticated users to their dashboard
    if (role === 'parent') {
      await navigateTo('/parent/dashboard')
    } else if (role === 'student') {
      await navigateTo('/student/dashboard')
    } else if (role === 'teacher') {
      await navigateTo('/dashboard')
    }
  } else {
    userRole.value = null
  }
})

// Optional: Fetch stats from API
const stats = ref<{
  totalStudents?: number
  totalProfiles?: number
  totalRecommendations?: number
  avgWordsPerStudent?: number
} | null>(null)

// TODO: Fetch stats from API
// const fetchStats = async () => {
//   try {
//     const config = useRuntimeConfig()
//     const apiUrl = config.public.apiUrl || 'http://localhost:8000'
//     const response = await $fetch(`${apiUrl}/api/stats/`)
//     stats.value = response
//   } catch (error) {
//     console.error('Failed to fetch stats:', error)
//   }
// }

// onMounted(() => {
//   fetchStats()
// })

useHead({
  title: 'Palabam - Personalized Vocabulary Recommendation Engine'
})
</script>
