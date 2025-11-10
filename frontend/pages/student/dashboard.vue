<template>
  <UContainer class="py-8">
    <UCard>
      <template #header>
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-3xl font-bold">My Progress</h1>
            <p class="text-gray-600 mt-2">Track your vocabulary journey</p>
          </div>
          <UButton
            to="/story-spark"
            color="primary"
            size="lg"
          >
            <UIcon name="i-heroicons-sparkles" class="mr-2" />
            Tell a Story
          </UButton>
        </div>
      </template>

      <!-- Loading State -->
      <div v-if="loading" class="text-center py-12">
        <UIcon name="i-heroicons-arrow-path" class="animate-spin text-4xl mb-4" />
        <p class="text-gray-600">Loading your progress...</p>
      </div>

      <!-- Progress Overview -->
      <div v-else class="space-y-8">
        <!-- Stats Cards -->
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
          <UCard>
            <div class="text-center">
              <div class="text-3xl font-bold text-primary">{{ progress?.vocabulary_level || 'Beginner' }}</div>
              <div class="text-sm text-gray-600 mt-1">Vocabulary Level</div>
            </div>
          </UCard>
          <UCard>
            <div class="text-center">
              <div class="text-3xl font-bold text-green-600">{{ progress?.current_streak || 0 }}</div>
              <div class="text-sm text-gray-600 mt-1">Day Streak</div>
            </div>
          </UCard>
          <UCard>
            <div class="text-center">
              <div class="text-3xl font-bold text-blue-600">{{ progress?.submission_count || 0 }}</div>
              <div class="text-sm text-gray-600 mt-1">Stories Told</div>
            </div>
          </UCard>
          <UCard>
            <div class="text-center">
              <div class="text-3xl font-bold text-purple-600">{{ progress?.total_points || 0 }}</div>
              <div class="text-sm text-gray-600 mt-1">Points Earned</div>
            </div>
          </UCard>
        </div>

        <!-- Vocabulary Level Progress -->
        <div>
          <h2 class="text-xl font-semibold mb-4">Vocabulary Level</h2>
          <UCard>
            <div class="space-y-2">
              <div class="flex items-center justify-between">
                <span class="text-sm font-medium">Your Progress</span>
                <UBadge
                  :color="getLevelColor(progress?.vocabulary_level)"
                  size="lg"
                >
                  {{ progress?.vocabulary_level || 'Beginner' }}
                </UBadge>
              </div>
              <UProgress
                :value="getLevelProgress(progress?.vocabulary_level)"
                :max="100"
                :color="getLevelColor(progress?.vocabulary_level)"
                class="mt-2"
              />
              <div class="flex justify-between text-xs text-gray-500 mt-1">
                <span>Beginner</span>
                <span>Intermediate</span>
                <span>Advanced</span>
                <span>Expert</span>
              </div>
            </div>
          </UCard>
        </div>

        <!-- Recommended Words -->
        <div>
          <h2 class="text-xl font-semibold mb-4">Words to Explore</h2>
          <div v-if="recommendedWords && recommendedWords.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            <UCard
              v-for="word in recommendedWords"
              :key="typeof word === 'string' ? word : word.word"
              class="p-4 hover:shadow-lg transition-shadow"
            >
              <div class="space-y-2">
                <div class="flex items-center justify-between">
                  <span class="font-semibold text-lg">
                    {{ typeof word === 'string' ? word : word.word }}
                  </span>
                  <UBadge
                    v-if="typeof word !== 'string' && word.relic_type"
                    :color="getRelicTypeColor(word.relic_type)"
                    variant="soft"
                    size="sm"
                  >
                    {{ word.relic_type }}
                  </UBadge>
                </div>
                <p v-if="typeof word !== 'string' && word.definition" class="text-sm text-gray-600">
                  {{ word.definition }}
                </p>
                <p v-if="typeof word !== 'string' && word.example" class="text-sm text-gray-500 italic">
                  "{{ word.example }}"
                </p>
              </div>
            </UCard>
          </div>
          <UCard v-else class="text-center py-8 text-gray-500">
            <p>No recommendations yet. Tell a story to get started!</p>
            <UButton
              to="/story-spark"
              color="primary"
              class="mt-4"
            >
              Tell Your First Story
            </UButton>
          </UCard>
        </div>

        <!-- Achievements -->
        <div v-if="achievements && achievements.length > 0">
          <h2 class="text-xl font-semibold mb-4">Achievements</h2>
          <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
            <UCard
              v-for="achievement in achievements"
              :key="achievement.id"
              class="text-center p-4"
            >
              <UIcon name="i-heroicons-trophy" class="text-4xl text-yellow-500 mb-2" />
              <div class="text-sm font-semibold capitalize">
                {{ formatAchievementType(achievement.achievement_type) }}
              </div>
              <div class="text-xs text-gray-500 mt-1">
                {{ formatDate(achievement.earned_at) }}
              </div>
            </UCard>
          </div>
        </div>

        <!-- Submission History -->
        <div>
          <h2 class="text-xl font-semibold mb-4">Recent Stories</h2>
          <div v-if="submissions && submissions.length > 0" class="space-y-2">
            <UCard
              v-for="submission in submissions.slice(0, 5)"
              :key="submission.id"
              class="p-4"
            >
              <div class="flex items-center justify-between">
                <div class="flex-1">
                  <div class="font-semibold">{{ formatDate(submission.created_at) }}</div>
                  <div class="text-sm text-gray-600 mt-1">
                    {{ submission.word_count }} words • {{ submission.type === 'story-spark' ? 'Story Spark' : 'Upload' }}
                  </div>
                </div>
                <UBadge
                  :color="submission.source === 'voice' ? 'blue' : 'gray'"
                  variant="soft"
                >
                  {{ submission.source }}
                </UBadge>
              </div>
            </UCard>
          </div>
          <UCard v-else class="text-center py-8 text-gray-500">
            <p>No stories yet. Start telling stories to see your history!</p>
          </UCard>
        </div>
      </div>
    </UCard>
  </UContainer>
</template>

<script setup lang="ts">
const config = useRuntimeConfig()
const apiUrl = config.public.apiUrl || 'http://localhost:8000'

// State
const loading = ref(true)
const progress = ref<any>(null)
const recommendedWords = ref<any[]>([])
const achievements = ref<any[]>([])
const submissions = ref<any[]>([])

// Get student ID from cookie or context
const studentId = useCookie('student_id').value || 'temp-student-id'

// Fetch all data
const fetchData = async () => {
  loading.value = true
  try {
    // Fetch progress
    const progressRes = await $fetch(`${apiUrl}/api/students/${studentId}/progress`)
    progress.value = progressRes

    // Fetch recommendations
    const recRes = await $fetch(`${apiUrl}/api/students/${studentId}/recommendations`)
    recommendedWords.value = recRes.recommended_words || []

    // Fetch achievements
    const achievementsRes = await $fetch(`${apiUrl}/api/students/${studentId}/achievements`)
    achievements.value = achievementsRes.achievements || []

    // Fetch submissions
    const submissionsRes = await $fetch(`${apiUrl}/api/students/${studentId}/submissions`)
    submissions.value = submissionsRes.submissions || []
  } catch (error) {
    console.error('Failed to fetch data:', error)
  } finally {
    loading.value = false
  }
}

const getLevelColor = (level?: string) => {
  const colors: Record<string, string> = {
    beginner: 'blue',
    intermediate: 'green',
    advanced: 'purple',
    expert: 'red'
  }
  return colors[level || ''] || 'gray'
}

const getLevelProgress = (level?: string) => {
  const levels: Record<string, number> = {
    beginner: 25,
    intermediate: 50,
    advanced: 75,
    expert: 100
  }
  return levels[level || 'beginner'] || 0
}

const getRelicTypeColor = (type: string) => {
  const colors: Record<string, string> = {
    whisper: 'gray',
    echo: 'blue',
    resonance: 'purple',
    thunder: 'red'
  }
  return colors[type] || 'gray'
}

const formatAchievementType = (type: string) => {
  return type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
}

const formatDate = (dateString: string) => {
  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  }).format(new Date(dateString))
}

onMounted(() => {
  fetchData()
})

useHead({
  title: 'My Progress - Palabam'
})
</script>

