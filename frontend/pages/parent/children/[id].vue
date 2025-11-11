<template>
  <UContainer class="py-8">
    <div class="mb-6">
      <UButton
        to="/parent/dashboard"
        variant="ghost"
        icon="i-heroicons-arrow-left"
        class="mb-4"
      >
        Back to Dashboard
      </UButton>
      <h1 class="text-3xl font-bold dark:text-white">{{ childName || 'Child Progress' }}</h1>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-12">
      <UIcon name="i-heroicons-arrow-path" class="animate-spin text-4xl mb-4" />
      <p class="text-gray-600 dark:text-gray-400">Loading progress...</p>
    </div>

    <!-- Error State -->
    <UAlert
      v-else-if="error"
      color="error"
      variant="soft"
      :title="error"
      class="mb-6"
    />

    <!-- Progress Content -->
    <div v-else class="space-y-6">
      <!-- Stats Cards -->
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <UCard>
          <div class="text-center">
            <div class="text-3xl font-bold text-primary">
              {{ progress?.vocabulary_level || 'Beginner' }}
            </div>
            <div class="text-sm text-gray-600 dark:text-gray-400 mt-1">Vocabulary Level</div>
          </div>
        </UCard>
        <UCard>
          <div class="text-center">
            <div class="text-3xl font-bold text-green-600">
              {{ progress?.current_streak || 0 }}
            </div>
            <div class="text-sm text-gray-600 dark:text-gray-400 mt-1">Day Streak</div>
          </div>
        </UCard>
        <UCard>
          <div class="text-center">
            <div class="text-3xl font-bold text-blue-600">
              {{ progress?.submission_count || 0 }}
            </div>
            <div class="text-sm text-gray-600 dark:text-gray-400 mt-1">Stories Told</div>
          </div>
        </UCard>
        <UCard>
          <div class="text-center">
            <div class="text-3xl font-bold text-purple-600">
              {{ progress?.total_points || 0 }}
            </div>
            <div class="text-sm text-gray-600 dark:text-gray-400 mt-1">Points Earned</div>
          </div>
        </UCard>
      </div>

      <!-- Vocabulary Level Progress -->
      <UCard>
        <template #header>
          <h2 class="text-xl font-semibold dark:text-white">Vocabulary Level</h2>
        </template>
        <div class="space-y-2">
          <div class="flex items-center justify-between">
            <span class="text-sm font-medium">Progress</span>
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
          <div class="flex justify-between text-xs text-gray-600 dark:text-gray-400 mt-1">
            <span>Beginner</span>
            <span>Intermediate</span>
            <span>Advanced</span>
            <span>Expert</span>
          </div>
        </div>
      </UCard>

      <!-- Recommended Words -->
      <UCard v-if="recommendedWords && recommendedWords.length > 0">
        <template #header>
          <h2 class="text-xl font-semibold dark:text-white">Words to Explore</h2>
        </template>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
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
              <p v-if="typeof word !== 'string' && word.definition" class="text-sm text-gray-600 dark:text-gray-400">
                {{ word.definition }}
              </p>
              <p v-if="typeof word !== 'string' && word.example" class="text-sm text-gray-600 dark:text-gray-400 italic">
                "{{ word.example }}"
              </p>
            </div>
          </UCard>
        </div>
      </UCard>

      <!-- Achievements -->
      <UCard v-if="achievements && achievements.length > 0">
        <template #header>
          <h2 class="text-xl font-semibold dark:text-white">Achievements</h2>
        </template>
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
            <div class="text-xs text-gray-600 dark:text-gray-400 mt-1">
              {{ formatDate(achievement.earned_at) }}
            </div>
          </UCard>
        </div>
      </UCard>

      <!-- Submission History -->
      <UCard>
        <template #header>
          <h2 class="text-xl font-semibold dark:text-white">Submission History</h2>
        </template>
        <div v-if="submissions && submissions.length > 0" class="space-y-2">
          <UCard
            v-for="submission in submissions"
            :key="submission.id"
            class="p-4"
          >
            <div class="flex items-center justify-between">
              <div class="flex-1">
                <div class="font-semibold dark:text-white">{{ formatDate(submission.created_at) }}</div>
                <div class="text-sm text-gray-600 dark:text-gray-400 mt-1">
                  {{ submission.word_count }} words • {{ formatSubmissionType(submission.type) }}
                </div>
                <div v-if="submission.content" class="text-sm text-gray-600 dark:text-gray-400 mt-2 line-clamp-2">
                  {{ submission.content.substring(0, 200) }}{{ submission.content.length > 200 ? '...' : '' }}
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
        <div v-else class="text-center py-8 text-gray-600 dark:text-gray-400">
          <p>No submissions yet</p>
        </div>
      </UCard>

      <!-- Session History -->
      <UCard v-if="sessions && sessions.length > 0">
        <template #header>
          <h2 class="text-xl font-semibold dark:text-white">Session History</h2>
        </template>
        <div class="space-y-2">
          <UCard
            v-for="session in sessions"
            :key="session.id"
            class="p-4"
          >
            <div class="flex items-center justify-between">
              <div>
                <div class="font-semibold dark:text-white">{{ formatDate(session.started_at) }}</div>
                <div class="text-sm text-gray-600 dark:text-gray-400 mt-1">
                  {{ session.activities_completed?.length || 0 }} activities completed
                </div>
                <div v-if="session.completed_at" class="text-xs text-gray-500 dark:text-gray-500 mt-1">
                  Completed: {{ formatDate(session.completed_at) }}
                </div>
              </div>
              <UBadge
                :color="session.completed_at ? 'success' : 'warning'"
                variant="soft"
              >
                {{ session.completed_at ? 'Completed' : 'In Progress' }}
              </UBadge>
            </div>
          </UCard>
        </div>
      </UCard>
    </div>
  </UContainer>
</template>

<script setup lang="ts">
definePageMeta({
  middleware: 'parent'
})

const route = useRoute()
const config = useRuntimeConfig()
const apiUrl = config.public.apiUrl || 'http://localhost:8000'

const childId = computed(() => route.params.id as string)
const loading = ref(true)
const error = ref<string | null>(null)
const childName = ref<string>('')
const progress = ref<any>(null)
const recommendedWords = ref<any[]>([])
const achievements = ref<any[]>([])
const submissions = ref<any[]>([])
const sessions = ref<any[]>([])

const fetchData = async () => {
  if (!childId.value) return

  loading.value = true
  error.value = null

  try {
    // Fetch progress
    const progressRes = await $fetch(`${apiUrl}/api/students/${childId.value}/progress`)
    progress.value = progressRes

    // Fetch student name
    const studentRes = await $fetch(`${apiUrl}/api/students/${childId.value}`)
    childName.value = studentRes.name || 'Child'

    // Fetch recommendations
    try {
      const recRes = await $fetch(`${apiUrl}/api/students/${childId.value}/recommendations`)
      recommendedWords.value = recRes.recommended_words || []
    } catch (err) {
      console.warn('Could not fetch recommendations:', err)
    }

    // Fetch achievements
    try {
      const achievementsRes = await $fetch(`${apiUrl}/api/students/${childId.value}/achievements`)
      achievements.value = achievementsRes.achievements || []
    } catch (err) {
      console.warn('Could not fetch achievements:', err)
    }

    // Fetch submissions
    try {
      const submissionsRes = await $fetch(`${apiUrl}/api/students/${childId.value}/submissions`)
      submissions.value = submissionsRes.submissions || []
    } catch (err) {
      console.warn('Could not fetch submissions:', err)
    }

    // Fetch sessions
    try {
      const sessionsRes = await $fetch(`${apiUrl}/api/students/${childId.value}/sessions`)
      sessions.value = sessionsRes.sessions || []
    } catch (err) {
      console.warn('Could not fetch sessions:', err)
    }
  } catch (err: any) {
    console.error('Failed to fetch data:', err)
    error.value = err.message || 'Failed to load child data. Please try again.'
  } finally {
    loading.value = false
  }
}

const getLevelColor = (level?: string) => {
  const colors: Record<string, string> = {
    beginner: 'primary',
    intermediate: 'teal',
    advanced: 'yellow',
    expert: 'pink'
  }
  return colors[level || 'beginner'] || 'gray'
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

const formatSubmissionType = (type: string) => {
  const types: Record<string, string> = {
    'story-spark': 'Story Spark',
    'upload': 'Upload',
    'teacher-upload': 'Teacher Upload'
  }
  return types[type] || type
}

const formatDate = (dateString: string) => {
  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: 'numeric',
    minute: 'numeric'
  }).format(new Date(dateString))
}

onMounted(() => {
  fetchData()
})

watch(() => route.params.id, () => {
  fetchData()
})

useHead({
  title: computed(() => `${childName.value || 'Child'} Progress - Palabam`)
})
</script>

