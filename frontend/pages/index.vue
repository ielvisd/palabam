<template>
  <UContainer>
    <div class="py-12">
      <div class="text-center mb-12">
        <h1 class="text-5xl font-bold mb-4">Palabam</h1>
        <p class="text-xl text-gray-600 mb-2">Personalized Vocabulary Recommendation Engine</p>
        <p class="text-gray-500">Automate vocabulary gap detection and provide personalized word recommendations for your students</p>
      </div>

      <!-- Feature Cards -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
        <UCard>
          <div class="text-center">
            <UIcon name="i-heroicons-document-text" class="text-4xl text-primary mb-4" />
            <h3 class="text-xl font-semibold mb-2">Analyze Transcripts</h3>
            <p class="text-gray-600">
              Upload or paste student conversation transcripts and writing samples for AI-powered analysis
            </p>
          </div>
        </UCard>

        <UCard>
          <div class="text-center">
            <UIcon name="i-heroicons-light-bulb" class="text-4xl text-primary mb-4" />
            <h3 class="text-xl font-semibold mb-2">Get Recommendations</h3>
            <p class="text-gray-600">
              Receive 5-7 personalized vocabulary words tailored to each student's proficiency level
            </p>
          </div>
        </UCard>

        <UCard>
          <div class="text-center">
            <UIcon name="i-heroicons-chart-bar" class="text-4xl text-primary mb-4" />
            <h3 class="text-xl font-semibold mb-2">Track Progress</h3>
            <p class="text-gray-600">
              View all student recommendations in one dashboard and export for lesson planning
            </p>
          </div>
        </UCard>
      </div>

      <!-- Action Buttons -->
      <div class="space-y-4">
        <div class="text-center mb-4">
          <h2 class="text-2xl font-semibold mb-2">For Educators</h2>
        </div>
        <div class="flex flex-col sm:flex-row gap-4 justify-center items-center">
          <UButton
            to="/spark"
            size="xl"
            color="primary"
            class="w-full sm:w-auto"
          >
            <UIcon name="i-heroicons-sparkles" class="mr-2" />
            Analyze Transcript
          </UButton>
          <UButton
            to="/dashboard"
            size="xl"
            variant="outline"
            class="w-full sm:w-auto"
          >
            <UIcon name="i-heroicons-squares-2x2" class="mr-2" />
            View Dashboard
          </UButton>
        </div>
        
        <div class="text-center my-8">
          <div class="border-t border-gray-300 my-6"></div>
          <h2 class="text-2xl font-semibold mb-2">For Students</h2>
        </div>
        <div class="flex flex-col sm:flex-row gap-4 justify-center items-center">
          <UButton
            to="/join-class"
            size="xl"
            color="primary"
            class="w-full sm:w-auto"
          >
            <UIcon name="i-heroicons-user-plus" class="mr-2" />
            Join Class
          </UButton>
          <UButton
            to="/story-spark"
            size="xl"
            variant="outline"
            class="w-full sm:w-auto"
          >
            <UIcon name="i-heroicons-sparkles" class="mr-2" />
            Tell a Story
          </UButton>
        </div>
      </div>

      <!-- Quick Stats (if available) -->
      <div v-if="stats" class="mt-12 grid grid-cols-1 md:grid-cols-4 gap-4">
        <UCard>
          <div class="text-center">
            <div class="text-3xl font-bold text-primary">{{ stats.totalStudents || 0 }}</div>
            <div class="text-sm text-gray-600 mt-1">Students</div>
          </div>
        </UCard>
        <UCard>
          <div class="text-center">
            <div class="text-3xl font-bold text-green-600">{{ stats.totalProfiles || 0 }}</div>
            <div class="text-sm text-gray-600 mt-1">Profiles Analyzed</div>
          </div>
        </UCard>
        <UCard>
          <div class="text-center">
            <div class="text-3xl font-bold text-blue-600">{{ stats.totalRecommendations || 0 }}</div>
            <div class="text-sm text-gray-600 mt-1">Words Recommended</div>
          </div>
        </UCard>
        <UCard>
          <div class="text-center">
            <div class="text-3xl font-bold text-purple-600">{{ stats.avgWordsPerStudent || 0 }}</div>
            <div class="text-sm text-gray-600 mt-1">Avg Words/Student</div>
          </div>
        </UCard>
      </div>
    </div>
  </UContainer>
</template>

<script setup lang="ts">
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
