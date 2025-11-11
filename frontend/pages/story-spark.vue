<template>
  <UContainer class="py-8">
    <UCard>
      <template #header>
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-3xl font-bold">Story Spark</h1>
            <p class="text-gray-600 mt-2">Tell me a story, and I'll help you discover new words!</p>
          </div>
          <div class="flex items-center gap-4">
            <USwitch
              v-model="isVoiceMode"
              @update:model-value="toggleInputMode"
              label="Voice Mode"
              color="primary"
            />
            <UButton
              v-if="isVoiceMode"
              @click="toggleTranscriptionMode"
              variant="ghost"
              color="neutral"
              size="sm"
            >
              {{ isRealTimeMode ? 'Real-time' : 'Record' }}
            </UButton>
          </div>
        </div>
      </template>

      <!-- Prompt Display -->
      <div class="mb-6">
        <UCard class="bg-gradient-to-r from-purple-50 to-blue-50 border-purple-200">
          <ClientOnly>
            <div class="space-y-2">
              <div class="flex items-center gap-2">
                <UIcon name="i-heroicons-sparkles" class="text-purple-600 text-xl" />
                <h3 class="text-lg font-semibold text-purple-900">Your Story Prompt</h3>
              </div>
              <p class="text-gray-700 text-base">{{ currentPrompt.text }}</p>
              <p class="text-sm text-gray-700 italic">
                💡 {{ currentPrompt.hint }}
              </p>
            </div>
            <template #fallback>
              <div class="space-y-2">
                <div class="flex items-center gap-2">
                  <UIcon name="i-heroicons-sparkles" class="text-purple-600 text-xl" />
                  <h3 class="text-lg font-semibold text-purple-900">Your Story Prompt</h3>
                </div>
                <p class="text-gray-700 text-base">{{ prompts[0].text }}</p>
                <p class="text-sm text-gray-700 italic">
                  💡 {{ prompts[0].hint }}
                </p>
              </div>
            </template>
          </ClientOnly>
        </UCard>
      </div>

      <!-- Input Section -->
      <div class="space-y-4">
        <!-- Voice Mode -->
        <div v-if="isVoiceMode" class="space-y-4">
          <div class="flex items-center gap-4">
            <UButton
              :color="isRecording ? 'red' : 'primary'"
              :disabled="isProcessing"
              @click="handleVoiceInput"
              size="xl"
              class="flex-1"
            >
              <template v-if="isRecording">
                <UIcon name="i-heroicons-stop-circle" class="mr-2" />
                Stop {{ isRealTimeMode ? 'Recording' : 'Recording' }}
              </template>
              <template v-else>
                <UIcon name="i-heroicons-microphone" class="mr-2" />
                Start {{ isRealTimeMode ? 'Speaking' : 'Recording' }}
              </template>
            </UButton>
          </div>
          
          <div v-if="isRecording" class="text-center">
            <div class="inline-flex items-center gap-2 text-red-600">
              <span class="animate-pulse">●</span>
              <span>{{ isRealTimeMode ? 'Listening...' : 'Recording...' }}</span>
            </div>
          </div>

          <!-- Real-time transcript display -->
          <div v-if="displayTranscript || interimTranscript" class="mt-4 p-4 bg-gray-50 rounded-lg min-h-[100px]">
            <p class="text-sm text-gray-600 mb-1">Your story:</p>
            <p class="text-base whitespace-pre-wrap">
              {{ transcript }}
              <span v-if="interimTranscript" class="text-gray-400 italic">
                {{ interimTranscript }}
              </span>
            </p>
            <p v-if="wordCount > 0" class="text-xs text-gray-600 mt-2">
              {{ wordCount }} words
            </p>
          </div>
        </div>

        <!-- Text Mode -->
        <div v-else>
          <UTextarea
            v-model="textInput"
            placeholder="Type your story here... Be creative and use your own words!"
            :rows="10"
            size="xl"
            :disabled="isProcessing"
            class="font-sans"
          />
          <p class="text-xs text-gray-600 mt-2">
            {{ textInput.length }} characters • {{ wordCount }} words
          </p>
        </div>

        <!-- Error Display -->
        <UAlert
          v-if="error"
          color="red"
          variant="soft"
          :title="error"
          class="mt-4"
          @close="error = null"
        />

        <!-- Submit Button -->
        <UButton
          :disabled="!canSubmit || isProcessing"
          :loading="isProcessing"
          size="xl"
          color="primary"
          block
          @click="submitStory"
        >
          {{ isProcessing ? 'Analyzing Your Story...' : 'Submit Story' }}
        </UButton>

        <!-- Processing Status -->
        <div v-if="isProcessing" class="text-center">
          <UProgress :value="processingProgress" class="mb-2" />
          <p class="text-sm text-gray-600">{{ processingStatus }}</p>
        </div>
      </div>

      <!-- Results -->
      <div v-if="submissionResult" class="mt-6">
        <UCard class="bg-secondary/10 border-secondary/30">
          <template #header>
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-2">
                <UIcon name="i-heroicons-check-circle" class="text-teal-700 text-2xl" />
                <h2 class="text-2xl font-bold text-navy">Analysis Complete!</h2>
              </div>
            </div>
          </template>
          
          <div class="space-y-6">
            <!-- Vocabulary Level Summary -->
            <div class="bg-white rounded-lg p-4 border border-gray-200">
              <div class="flex items-center justify-between">
                <div>
                  <p class="text-sm text-gray-600 mb-1">Vocabulary Level</p>
                  <div class="flex flex-col gap-1">
                    <UBadge
                      :color="getLevelColor(submissionResult.vocabulary_level)"
                      size="xl"
                      variant="soft"
                    >
                      {{ formatVocabularyLevel(submissionResult.vocabulary_level) }}
                    </UBadge>
                    <span v-if="submissionResult.vocabulary_level" class="text-xs text-gray-500">
                      {{ getVocabularyLevelContext(submissionResult.vocabulary_level) }}
                    </span>
                  </div>
                </div>
                <div class="text-right">
                  <p class="text-sm text-gray-600 mb-1">Words Analyzed</p>
                  <p class="text-2xl font-bold text-primary">{{ wordCount }}</p>
                </div>
              </div>
            </div>

            <!-- Recommended Words -->
            <div v-if="submissionResult.recommended_words && submissionResult.recommended_words.length > 0">
              <div class="flex items-center gap-2 mb-4">
                <UIcon name="i-heroicons-sparkles" class="text-teal-700 text-xl" />
                <h3 class="text-xl font-bold text-navy">Recommended Words ({{ submissionResult.recommended_words.length }})</h3>
              </div>
              <p class="text-sm text-gray-600 mb-4">
                These words are personalized to your writing level and will help expand your vocabulary.
              </p>
              <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <UCard
                  v-for="word in submissionResult.recommended_words"
                  :key="typeof word === 'string' ? word : word.word"
                  class="p-4 hover:shadow-lg transition-all border-l-4"
                  :class="getWordCardBorderClass(word)"
                >
                  <div class="space-y-3">
                    <div class="flex items-start justify-between">
                      <div class="flex-1">
                        <h4 class="font-bold text-lg text-navy mb-1">
                          {{ typeof word === 'string' ? word : word.word }}
                        </h4>
                        <div class="flex items-center gap-2 flex-wrap">
                          <UBadge
                            v-if="typeof word !== 'string' && word.relic_type"
                            :color="getRelicTypeColor(word.relic_type)"
                            variant="soft"
                            size="xs"
                          >
                            {{ word.relic_type }}
                          </UBadge>
                          <UBadge
                            v-if="typeof word !== 'string' && word.grade_level"
                            color="teal"
                            variant="soft"
                            size="xs"
                          >
                            {{ word.grade_level }} Grade
                          </UBadge>
                          <span v-if="typeof word !== 'string' && word.difficulty_score" class="text-xs text-gray-600">
                            Difficulty: {{ word.difficulty_score }}/100
                          </span>
                        </div>
                      </div>
                    </div>
                    
                    <p v-if="typeof word !== 'string' && word.definition" class="text-sm text-gray-700 leading-relaxed">
                      {{ word.definition }}
                    </p>
                    
                    <p v-if="typeof word !== 'string' && word.example" class="text-sm text-gray-600 italic border-l-2 border-primary pl-3 py-1 bg-gray-50 rounded">
                      "{{ word.example }}"
                    </p>
                    
                    <div v-if="typeof word !== 'string' && word.rationale" class="text-xs text-gray-600 bg-teal/10 p-2 rounded flex items-start gap-2">
                      <UIcon name="i-heroicons-light-bulb" class="text-teal-700 mt-0.5 flex-shrink-0" />
                      <span>{{ word.rationale }}</span>
                    </div>
                  </div>
                </UCard>
              </div>
            </div>

            <div class="flex gap-4 pt-4">
              <UButton
                to="/dashboard"
                color="primary"
                size="lg"
                block
                icon="i-heroicons-chart-bar"
              >
                View in Dashboard
              </UButton>
              <UButton
                @click="startNewStory"
                variant="outline"
                color="neutral"
                size="lg"
                block
                icon="i-heroicons-pencil"
              >
                Tell Another Story
              </UButton>
            </div>
          </div>
        </UCard>
      </div>
    </UCard>
  </UContainer>
</template>

<script setup lang="ts">
definePageMeta({
  middleware: 'student'
})

const {
  isVoiceMode,
  isRecording,
  isRealTimeMode,
  transcript,
  interimTranscript,
  displayTranscript,
  error,
  startRecording,
  stopRecording,
  toggleInputMode,
  toggleTranscriptionMode
} = useStorySpark()

const textInput = ref('')
const isProcessing = ref(false)
const processingProgress = ref(0)
const processingStatus = ref('')
const submissionResult = ref<{
  vocabulary_level: string
  recommended_words: Array<string | {
    word: string
    definition?: string
    example?: string
    difficulty_score?: number
    relic_type?: string
  }>
  points_earned?: number
} | null>(null)

// Story prompts (pedagogically-sound, engaging scenarios)
const prompts = [
  {
    text: "Tell me about your perfect day. What would you do from morning to night?",
    hint: "Use descriptive words to paint a picture!"
  },
  {
    text: "You're a detective solving a mystery. What case are you working on?",
    hint: "Think about clues, suspects, and how you'd solve it."
  },
  {
    text: "Describe a time when you had to be brave or face a challenge.",
    hint: "What made it difficult? How did you handle it?"
  },
  {
    text: "If you could have any superpower, what would it be and how would you use it?",
    hint: "Be creative and explain your choice!"
  },
  {
    text: "Tell me about your favorite hobby or activity. Why do you love it?",
    hint: "Use specific details and emotions."
  }
]

// Initialize with first prompt (deterministic) to ensure server and client match
// This prevents hydration mismatches
const currentPrompt = ref(prompts[0])

// Randomize prompt after hydration completes
// Using requestAnimationFrame ensures this runs after Vue has finished hydrating
onMounted(() => {
  requestAnimationFrame(() => {
    currentPrompt.value = prompts[Math.floor(Math.random() * prompts.length)]
  })
})

const wordCount = computed(() => {
  if (isVoiceMode.value) {
    const fullText = transcript.value + (interimTranscript.value || '')
    return fullText.trim().split(/\s+/).filter(word => word.length > 0).length
  }
  return textInput.value.trim().split(/\s+/).filter(word => word.length > 0).length
})

const canSubmit = computed(() => {
  if (isVoiceMode.value) {
    return transcript.value.trim().length > 0 && wordCount.value >= 10
  }
  return textInput.value.trim().length > 0 && wordCount.value >= 10
})

const handleVoiceInput = () => {
  if (isRecording.value) {
    stopRecording()
  } else {
    startRecording()
  }
}

const submitStory = async () => {
  if (!canSubmit.value) return

  isProcessing.value = true
  processingProgress.value = 0
  processingStatus.value = 'Preparing your story...'

  try {
    const inputText = isVoiceMode.value ? transcript.value : textInput.value

    // Get student ID from auth (authentication required)
    const { getStudentId } = useAuth()
    const studentId = await getStudentId()
    
    if (!studentId) {
      error.value = 'You must be signed in to submit a story. Please sign in first.'
      processingProgress.value = 0
      processingStatus.value = ''
      return
    }

    processingProgress.value = 30
    processingStatus.value = 'Analyzing your vocabulary...'

    const config = useRuntimeConfig()
    const apiUrl = config.public.apiUrl || 'http://localhost:8000'
    
    // Call profile API to analyze transcript and generate recommendations
    const profileResponse = await $fetch(`${apiUrl}/api/profile/`, {
      method: 'POST',
      body: {
        transcript: inputText,
        student_id: studentId,
        inputMode: isVoiceMode.value ? 'voice' : 'text'
      }
    }) as any

    processingProgress.value = 80
    processingStatus.value = 'Generating recommendations...'
    
    // Also create submission record for history
    const response = await $fetch(`${apiUrl}/api/submissions/`, {
      method: 'POST',
      body: {
        student_id: studentId,
        type: 'story-spark',
        content: inputText,
        source: isVoiceMode.value ? 'voice' : 'text'
      }
    })

    processingProgress.value = 100
    processingStatus.value = 'Complete!'

    const result = response as any
    // Use profile response for vocabulary level and recommendations
    submissionResult.value = {
      vocabulary_level: profileResponse.vocabulary_level || result.vocabulary_level || 'intermediate',
      recommended_words: profileResponse.recommended_words || result.recommended_words || [],
      points_earned: 10 + Math.floor(wordCount.value / 100) * 5,
      profile_id: profileResponse.profile_id,
      resonance_data: profileResponse.resonance_data
    }

    // Reset form after a delay
    setTimeout(() => {
      textInput.value = ''
      // Don't reset transcript immediately - let user see results
      isProcessing.value = false
    }, 3000)
  } catch (err: any) {
    // Better error handling
    console.error('Submission error:', err)
    
    if (err.statusCode === 400 || err.status === 400) {
      error.value = err.data?.detail || err.message || 'Invalid story. Please check your input and try again.'
    } else if (err.statusCode === 404 || err.status === 404) {
      error.value = 'Student not found. Please join a class first.'
    } else if (err.statusCode >= 500 || (err.status && err.status >= 500)) {
      error.value = 'Server error. Please try again later.'
    } else if (err.message?.includes('network') || err.message?.includes('fetch') || err.message?.includes('Failed to fetch')) {
      error.value = 'Network error. Please check your connection and try again.'
    } else {
      error.value = err.data?.detail || err.message || 'Failed to submit story. Please try again.'
    }
    isProcessing.value = false
    processingProgress.value = 0
    processingStatus.value = ''
  }
}

const startNewStory = () => {
  submissionResult.value = null
  textInput.value = ''
  transcript.value = ''
  interimTranscript.value = ''
  currentPrompt.value = prompts[Math.floor(Math.random() * prompts.length)]
}

const formatVocabularyLevel = (level?: string) => {
  if (!level) return 'Analyzing...'
  // Make it clear it's a grade level
  if (level.includes('-') || level === '12+') {
    return `${level} grade level`
  }
  // Legacy support
  return level.charAt(0).toUpperCase() + level.slice(1)
}

const getVocabularyLevelContext = (level?: string) => {
  if (!level) return ''
  
  // Grade level mapping for context
  const gradeOrder = ['K-1', '2-3', '4-5', '6-7', '8-9', '10-11', '12+']
  const levelIndex = gradeOrder.indexOf(level)
  
  if (levelIndex === -1) return '' // Legacy levels, no context
  
  // Provide context based on typical expectations
  if (levelIndex <= 1) return '(Early elementary)'
  if (levelIndex <= 2) return '(Elementary)'
  if (levelIndex <= 3) return '(Middle school)'
  if (levelIndex <= 4) return '(High school)'
  return '(Advanced)'
}

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

const getRelicTypeColor = (type?: string) => {
  const colors: Record<string, string> = {
    whisper: 'gray',
    echo: 'primary',
    resonance: 'teal',
    thunder: 'pink'
  }
  return colors[type || ''] || 'gray'
}

const getWordCardBorderClass = (word: any): string => {
  if (typeof word === 'string') return 'border-l-primary'
  const type = word.relic_type || 'echo'
  const colors: Record<string, string> = {
    whisper: 'border-l-gray-400',
    echo: 'border-l-primary',
    resonance: 'border-l-secondary',
    thunder: 'border-l-pink'
  }
  return colors[type] || 'border-l-primary'
}

useHead({
  title: 'Story Spark - Palabam'
})
</script>

