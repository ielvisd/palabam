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

      <!-- Error State -->
      <UAlert
        v-else-if="error"
        color="red"
        variant="soft"
        :title="error"
        class="mb-6"
      >
        <template #actions>
          <UButton
            color="neutral"
            variant="ghost"
            size="xs"
            @click="fetchData"
            class="mt-2"
          >
            Retry
          </UButton>
        </template>
      </UAlert>

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
              <div class="flex justify-between text-xs text-gray-600 mt-1">
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
                    {{ getRelicTypeLabel(word.relic_type) }}
                  </UBadge>
                </div>
                <p v-if="typeof word !== 'string' && word.definition" class="text-sm text-gray-600">
                  {{ word.definition }}
                </p>
                <p v-if="typeof word !== 'string' && word.example" class="text-sm text-gray-600 italic">
                  "{{ word.example }}"
                </p>
              </div>
            </UCard>
          </div>
          <UCard v-else class="text-center py-8 text-gray-600">
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
              <div class="text-xs text-gray-600 mt-1">
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
          <UCard v-else class="text-center py-8 text-gray-600">
            <p>No stories yet. Start telling stories to see your history!</p>
          </UCard>
        </div>
      </div>
    </UCard>
  </UContainer>
</template>

<script setup lang="ts">
definePageMeta({
  middleware: 'student'
})

const config = useRuntimeConfig()
const apiUrl = config.public.apiUrl || 'http://localhost:8000'

// State
const loading = ref(true)
const progress = ref<any>(null)
const recommendedWords = ref<any[]>([])
const achievements = ref<any[]>([])
const submissions = ref<any[]>([])

// Get student ID from auth
const { getStudentId } = useAuth()
const studentId = ref<string | null>(null)
const error = ref<string | null>(null)

// Helper function to check if error is a connection error
const isConnectionError = (err: any): boolean => {
  if (!err) return false
  const message = err.message || err.toString() || ''
  const statusCode = err.statusCode || err.status
  return (
    message.includes('Failed to fetch') ||
    message.includes('ERR_CONNECTION_REFUSED') ||
    message.includes('NetworkError') ||
    message.includes('network') ||
    statusCode === 0 ||
    (err.cause && err.cause.code === 'ECONNREFUSED')
  )
}

// Fetch all data
const fetchData = async () => {
  if (!studentId.value) return
  
  loading.value = true
  error.value = null
  try {
    // Fetch progress
    const progressRes = await $fetch(`${apiUrl}/api/students/${studentId.value}/progress`)
    progress.value = progressRes

    // Fetch recommendations (optional - don't fail if this fails)
    try {
      const recRes = await $fetch(`${apiUrl}/api/students/${studentId.value}/recommendations`)
      recommendedWords.value = recRes.recommended_words || []
    } catch (err) {
      console.warn('Could not fetch recommendations:', err)
      recommendedWords.value = []
    }

    // Fetch achievements (optional - don't fail if this fails)
    try {
      const achievementsRes = await $fetch(`${apiUrl}/api/students/${studentId.value}/achievements`)
      achievements.value = achievementsRes.achievements || []
    } catch (err) {
      console.warn('Could not fetch achievements:', err)
      achievements.value = []
    }

    // Fetch submissions (optional - don't fail if this fails)
    try {
      const submissionsRes = await $fetch(`${apiUrl}/api/students/${studentId.value}/submissions`)
      submissions.value = submissionsRes.submissions || []
    } catch (err) {
      console.warn('Could not fetch submissions:', err)
      submissions.value = []
    }
  } catch (err: any) {
    console.error('Failed to fetch data:', err)
    
    if (isConnectionError(err)) {
      error.value = `Unable to connect to the backend API at ${apiUrl}. Please ensure the backend server is running.`
    } else {
      error.value = err.data?.detail || err.message || 'Failed to load dashboard data. Please try again.'
    }
  } finally {
    loading.value = false
  }
}

// Initialize student ID and fetch data
onMounted(async () => {
  const id = await getStudentId()
  studentId.value = id || useCookie('student_id').value || null
  
  if (studentId.value) {
    await fetchData()
  } else {
    error.value = 'Student ID not found. Please join a class first.'
    loading.value = false
  }
})

const getLevelColor = (level?: string) => {
  // Grade levels: K-1, 2-3, 4-5, 6-7, 8-9, 10-11, 12+
  const colors: Record<string, string> = {
    'K-1': 'primary',
    '2-3': 'primary',
    '4-5': 'teal',
    '6-7': 'teal',
    '8-9': 'yellow',
    '10-11': 'yellow',
    '12+': 'pink',
    // Legacy support for old categories
    beginner: 'primary',
    intermediate: 'teal',
    advanced: 'yellow',
    expert: 'pink'
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

const getRelicTypeLabel = (type?: string) => {
  if (!type) return 'Basic'
  const labels: Record<string, string> = {
    whisper: 'Easy',
    echo: 'Basic',
    resonance: 'Intermediate',
    thunder: 'Advanced'
  }
  return labels[type] || 'Basic'
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

useHead({
  title: 'My Progress - Palabam'
})
</script>

