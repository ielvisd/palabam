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
              size="sm"
            >
              {{ isRealTimeMode ? 'Real-time' : 'Record' }}
            </UButton>
          </div>
        </div>
      </template>

      <!-- Prompt Display -->
      <div v-if="currentPrompt" class="mb-6">
        <UCard class="bg-gradient-to-r from-purple-50 to-blue-50 border-purple-200">
          <div class="space-y-2">
            <div class="flex items-center gap-2">
              <UIcon name="i-heroicons-sparkles" class="text-purple-600 text-xl" />
              <h3 class="text-lg font-semibold text-purple-900">Your Story Prompt</h3>
            </div>
            <p class="text-gray-700 text-base">{{ currentPrompt.text }}</p>
            <p v-if="currentPrompt.hint" class="text-sm text-gray-600 italic">
              💡 {{ currentPrompt.hint }}
            </p>
          </div>
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
              {{ displayTranscript }}
              <span v-if="interimTranscript" class="text-gray-400 italic">
                {{ interimTranscript }}
              </span>
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
          <p class="text-xs text-gray-500 mt-2">
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
        <UCard class="bg-green-50 border-green-200">
          <template #header>
            <div class="flex items-center gap-2">
              <UIcon name="i-heroicons-check-circle" class="text-green-600 text-xl" />
              <h2 class="text-xl font-bold text-green-900">Story Submitted!</h2>
            </div>
          </template>
          
          <div class="space-y-4">
            <div>
              <h3 class="font-semibold mb-2">Your Vocabulary Level:</h3>
              <UBadge
                :color="getLevelColor(submissionResult.vocabulary_level)"
                size="lg"
                variant="soft"
              >
                {{ submissionResult.vocabulary_level || 'Analyzing...' }}
              </UBadge>
            </div>

            <div v-if="submissionResult.recommended_words && submissionResult.recommended_words.length > 0">
              <h3 class="font-semibold mb-2">Words to Explore:</h3>
              <div class="flex flex-wrap gap-2">
                <UBadge
                  v-for="word in submissionResult.recommended_words"
                  :key="word"
                  color="primary"
                  variant="soft"
                  size="lg"
                >
                  {{ word }}
                </UBadge>
              </div>
            </div>

            <div class="flex gap-4 pt-4">
              <UButton
                to="/student/dashboard"
                color="primary"
                size="lg"
                block
              >
                View My Progress
              </UButton>
              <UButton
                @click="startNewStory"
                variant="outline"
                size="lg"
                block
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
  recommended_words: string[]
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

const currentPrompt = ref(prompts[Math.floor(Math.random() * prompts.length)])

const wordCount = computed(() => {
  const text = isVoiceMode.value ? displayTranscript.value : textInput.value
  return text.trim().split(/\s+/).filter(word => word.length > 0).length
})

const canSubmit = computed(() => {
  if (isVoiceMode.value) {
    return displayTranscript.value.length > 0 && wordCount.value >= 10
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
    const inputText = isVoiceMode.value ? displayTranscript.value : textInput.value

    // Get student ID from storage or context (simplified for now)
    const studentId = useCookie('student_id').value || 'temp-student-id'

    processingProgress.value = 30
    processingStatus.value = 'Analyzing your vocabulary...'

    const config = useRuntimeConfig()
    const apiUrl = config.public.apiUrl || 'http://localhost:8000'
    
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

    submissionResult.value = {
      vocabulary_level: response.vocabulary_level || 'intermediate',
      recommended_words: response.recommended_words || [],
      points_earned: 10 + Math.floor(wordCount.value / 100) * 5
    }

    // Reset form after a delay
    setTimeout(() => {
      textInput.value = ''
      transcript.value = ''
      interimTranscript.value = ''
      isProcessing.value = false
    }, 3000)
  } catch (err: any) {
    error.value = err.message || 'Failed to submit story. Please try again.'
    isProcessing.value = false
  }
}

const startNewStory = () => {
  submissionResult.value = null
  textInput.value = ''
  transcript.value = ''
  interimTranscript.value = ''
  currentPrompt.value = prompts[Math.floor(Math.random() * prompts.length)]
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

useHead({
  title: 'Story Spark - Palabam'
})
</script>

