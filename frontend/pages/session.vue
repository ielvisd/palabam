<template>
  <UContainer class="py-8">
    <UCard>
      <template #header>
        <div class="flex items-center justify-between">
          <h1 class="text-2xl font-bold">Daily Vocab Drill</h1>
          <div class="flex items-center gap-4">
            <div class="text-sm text-gray-600">
              <span class="font-semibold">{{ timeRemainingFormatted }}</span>
            </div>
            <UProgress :value="progressPercentage" :max="100" class="w-32" />
          </div>
        </div>
      </template>

      <!-- Session Start Screen -->
      <div v-if="!sessionStarted" class="text-center space-y-6">
        <div>
          <h2 class="text-xl font-semibold mb-2">Ready to start your session?</h2>
          <p class="text-gray-600">
            You'll practice {{ totalWords }} words in 6 different activities
          </p>
        </div>
        <UButton
          size="xl"
          color="primary"
          @click="startSession"
          :loading="loading"
        >
          Start Session
        </UButton>
      </div>

      <!-- Active Session -->
      <div v-else-if="currentWord && !sessionComplete">
        <!-- Progress Display -->
        <div class="mb-6">
          <div class="flex items-center justify-between mb-2">
            <span class="text-sm font-medium">
              Word {{ currentWordIndex + 1 }} of {{ totalWords }}
            </span>
            <span class="text-sm text-gray-600">
              {{ stats.mastered }}/{{ stats.total }} mastered
            </span>
          </div>
          <UProgress :value="currentWordIndex + 1" :max="totalWords" />
        </div>

        <!-- Current Activity Component -->
        <component
          :is="currentActivityComponent"
          :word="currentWord"
          :activity-index="currentActivityIndex"
          @complete="handleActivityComplete"
          @skip="handleActivitySkip"
        />
      </div>

      <!-- Session Complete -->
      <div v-else-if="sessionComplete" class="text-center space-y-6">
        <UConfetti />
        <div>
          <h2 class="text-2xl font-bold text-green-600 mb-2">Session Complete!</h2>
          <p class="text-gray-600 mb-4">
            Great job! You've completed all activities.
          </p>
          <div class="grid grid-cols-3 gap-4 mb-6">
            <div class="p-4 bg-gray-50 rounded-lg">
              <div class="text-2xl font-bold text-primary">{{ stats.mastered }}</div>
              <div class="text-sm text-gray-600">Mastered</div>
            </div>
            <div class="p-4 bg-gray-50 rounded-lg">
              <div class="text-2xl font-bold text-blue-600">{{ stats.inProgress }}</div>
              <div class="text-sm text-gray-600">In Progress</div>
            </div>
            <div class="p-4 bg-gray-50 rounded-lg">
              <div class="text-2xl font-bold text-purple-600">{{ Math.round(stats.masteryPercentage) }}%</div>
              <div class="text-sm text-gray-600">Mastery</div>
            </div>
          </div>
          <div class="flex gap-4 justify-center">
            <UButton to="/ledger" color="primary" size="lg">
              View Progress
            </UButton>
            <UButton @click="resetSession" variant="outline" size="lg">
              New Session
            </UButton>
          </div>
        </div>
      </div>

      <!-- Loading State -->
      <div v-else class="text-center">
        <UIcon name="i-heroicons-arrow-path" class="animate-spin text-4xl mb-4" />
        <p>Loading session...</p>
      </div>
    </UCard>
  </UContainer>
</template>

<script setup lang="ts">
import { useSRS, type Word } from '@/composables/useSRS'
import { useVocabInput } from '@/composables/useVocabInput'
import ActivityFlashcard from '@/components/activities/ActivityFlashcard.vue'
import ActivityMultipleChoice from '@/components/activities/ActivityMultipleChoice.vue'
import ActivitySpelling from '@/components/activities/ActivitySpelling.vue'
import ActivityFillBlank from '@/components/activities/ActivityFillBlank.vue'
import ActivitySynonym from '@/components/activities/ActivitySynonym.vue'
import ActivitySentence from '@/components/activities/ActivitySentence.vue'

const {
  loading,
  sessionWords,
  fetchDueWords,
  updateProgress,
  getProgressStats,
  resetSession: resetSRS
} = useSRS()

const { speak } = useVocabInput()

// Session state
const sessionStarted = ref(false)
const sessionComplete = ref(false)
const currentWordIndex = ref(0)
const currentActivityIndex = ref(0)
const timeRemaining = ref(600) // 10 minutes in seconds
const timerInterval = ref<NodeJS.Timeout | null>(null)

// Activities list
const activities = [
  'flashcard',
  'multiple-choice',
  'spelling',
  'fill-blank',
  'synonym',
  'sentence'
]

const currentWord = computed(() => {
  if (sessionWords.value.length === 0) return null
  return sessionWords.value[currentWordIndex.value]
})

const totalWords = computed(() => sessionWords.value.length)

const currentActivity = computed(() => {
  return activities[currentActivityIndex.value]
})

const currentActivityComponent = computed(() => {
  const componentMap: Record<string, any> = {
    'flashcard': ActivityFlashcard,
    'multiple-choice': ActivityMultipleChoice,
    'spelling': ActivitySpelling,
    'fill-blank': ActivityFillBlank,
    'synonym': ActivitySynonym,
    'sentence': ActivitySentence
  }
  return componentMap[currentActivity.value] || ActivityFlashcard
})

const progressPercentage = computed(() => {
  if (totalWords.value === 0) return 0
  return ((currentWordIndex.value + 1) / totalWords.value) * 100
})

const timeRemainingFormatted = computed(() => {
  const minutes = Math.floor(timeRemaining.value / 60)
  const seconds = timeRemaining.value % 60
  return `${minutes}:${seconds.toString().padStart(2, '0')}`
})

const stats = computed(() => getProgressStats())

const startSession = async () => {
  try {
    // TODO: Get student ID from auth
    const studentId = 'temp-student-id'
    
    await fetchDueWords(studentId, 4, 8)
    
    if (sessionWords.value.length === 0) {
      // No words available
      return
    }
    
    sessionStarted.value = true
    startTimer()
  } catch (error) {
    console.error('Failed to start session:', error)
  }
}

const startTimer = () => {
  timerInterval.value = setInterval(() => {
    timeRemaining.value--
    
    if (timeRemaining.value <= 0) {
      endSession()
    }
  }, 1000)
}

const handleActivityComplete = async (quality: number) => {
  if (!currentWord.value) return
  
  try {
    // Update SRS progress
    const studentId = 'temp-student-id'
    await updateProgress(studentId, currentWord.value.id, quality)
    
    // Move to next activity or word
    await nextStep()
  } catch (error) {
    console.error('Failed to update progress:', error)
  }
}

const handleActivitySkip = async () => {
  // Skip current activity, move to next
  await nextStep()
}

const nextStep = async () => {
  // Move to next activity
  currentActivityIndex.value++
  
  // If all activities done for this word, move to next word
  if (currentActivityIndex.value >= activities.length) {
    currentActivityIndex.value = 0
    currentWordIndex.value++
    
    // If all words done, complete session
    if (currentWordIndex.value >= totalWords.value) {
      endSession()
      return
    }
  }
}

const endSession = () => {
  if (timerInterval.value) {
    clearInterval(timerInterval.value)
    timerInterval.value = null
  }
  sessionComplete.value = true
}

const resetSession = () => {
  sessionStarted.value = false
  sessionComplete.value = false
  currentWordIndex.value = 0
  currentActivityIndex.value = 0
  timeRemaining.value = 600
  resetSRS()
  
  if (timerInterval.value) {
    clearInterval(timerInterval.value)
    timerInterval.value = null
  }
}

onUnmounted(() => {
  if (timerInterval.value) {
    clearInterval(timerInterval.value)
  }
})

useHead({
  title: 'Daily Session - Palabam'
})
</script>

