<template>
  <div class="space-y-6">
    <h2 class="text-xl font-semibold text-center">Sentence Generation</h2>
    
    <UCard>
      <div class="space-y-6">
        <div class="text-center">
          <p class="text-2xl font-bold mb-2">{{ word.word }}</p>
          <p class="text-gray-600 mb-4">
            Use <strong>{{ word.word }}</strong> in a sentence about your day
          </p>
        </div>

        <div class="relative">
          <UTextarea
            v-model="userSentence"
            placeholder="Type your sentence here..."
            :rows="4"
            size="xl"
            :disabled="submitted || isRecordingAudio"
          />
          <UButton
            v-if="!isRecordingAudio"
            @click="handleAudioInput"
            :disabled="submitted"
            variant="ghost"
            color="primary"
            size="sm"
            class="absolute top-2 right-2"
            :title="'Start voice input'"
          >
            <UIcon name="i-heroicons-microphone" class="w-5 h-5" />
          </UButton>
          <UButton
            v-else
            @click="stopAudioRecording"
            :disabled="submitted"
            color="red"
            size="sm"
            class="absolute top-2 right-2"
            :title="'Stop recording'"
          >
            <UIcon name="i-heroicons-stop-circle" class="w-5 h-5" />
          </UButton>
        </div>
        <div v-if="isRecordingAudio" class="text-center">
          <div class="inline-flex items-center gap-2 text-red-600">
            <span class="animate-pulse">●</span>
            <span class="text-sm">Recording...</span>
          </div>
        </div>

        <div v-if="submitted" class="space-y-4">
          <div class="p-4 bg-gray-50 rounded-lg">
            <div class="flex items-center justify-between mb-2">
              <span class="font-semibold">Your Sentence:</span>
              <UBadge :color="score >= 0.7 ? 'green' : score >= 0.4 ? 'yellow' : 'red'">
                {{ Math.round(score * 100) }}% Score
              </UBadge>
            </div>
            <p class="text-gray-700">{{ userSentence }}</p>
          </div>

          <div v-if="feedback" class="p-4 bg-blue-50 rounded-lg">
            <p class="text-sm text-blue-800">{{ feedback }}</p>
          </div>

          <UButton
            @click="handleNext"
            color="primary"
            size="lg"
            block
          >
            Continue
          </UButton>
        </div>

        <div v-else class="text-center">
          <UButton
            @click="submitSentence"
            color="primary"
            size="lg"
            :disabled="!userSentence.trim()"
            :loading="scoring"
          >
            Submit Sentence
          </UButton>
        </div>
      </div>
    </UCard>
  </div>
</template>

<script setup lang="ts">
import { useVocabInput } from '@/composables/useVocabInput'

const props = defineProps<{
  word: {
    word: string
    definition: string
    example?: string
  }
  activityIndex: number
}>()

const emit = defineEmits<{
  complete: [quality: number]
  skip: []
}>()

const { speak } = useVocabInput()

// Audio input composable
const {
  isRecording: isRecordingAudio,
  transcript: audioTranscript,
  getCurrentTranscript,
  startRecording: startAudioRecording,
  stopRecording: stopAudioRecording,
  clearTranscript: clearAudioTranscript
} = useAudioInput()

const userSentence = ref('')
const submitted = ref(false)
const scoring = ref(false)
const score = ref(0)
const feedback = ref('')

// Handle audio input
const handleAudioInput = () => {
  startAudioRecording()
}

// Watch for transcript updates and append to userSentence
watch(audioTranscript, (newTranscript) => {
  if (newTranscript && isRecordingAudio.value) {
    const currentText = userSentence.value.trim()
    const transcriptText = newTranscript.trim()
    if (transcriptText && !currentText.endsWith(transcriptText)) {
      userSentence.value = currentText ? `${currentText} ${transcriptText}` : transcriptText
    }
  }
})

// Watch for recording to stop and finalize any remaining transcript
watch(isRecordingAudio, (recording) => {
  if (!recording) {
    const finalTranscript = getCurrentTranscript.value.trim()
    if (finalTranscript) {
      const currentText = userSentence.value.trim()
      if (finalTranscript && !currentText.endsWith(finalTranscript)) {
        userSentence.value = currentText ? `${currentText} ${finalTranscript}` : finalTranscript
      }
    }
    clearAudioTranscript()
  }
})

const submitSentence = async () => {
  if (!userSentence.value.trim()) return
  
  scoring.value = true
  
  try {
    // Score the sentence (would call backend API)
    // For now, do basic validation
    const sentence = userSentence.value.toLowerCase()
    const wordLower = props.word.word.toLowerCase()
    
    // Check if word is used
    const usesWord = sentence.includes(wordLower)
    
    // Basic grammar check (simplified)
    const hasCapital = /^[A-Z]/.test(userSentence.value.trim())
    const hasPeriod = /[.!?]$/.test(userSentence.value.trim())
    
    // Calculate score
    let calculatedScore = 0
    if (usesWord) calculatedScore += 0.5
    if (hasCapital) calculatedScore += 0.2
    if (hasPeriod) calculatedScore += 0.2
    if (sentence.length > 20) calculatedScore += 0.1
    
    score.value = Math.min(1.0, calculatedScore)
    
    // Generate feedback
    if (score.value >= 0.7) {
      feedback.value = 'Great job! You used the word correctly.'
    } else if (score.value >= 0.4) {
      feedback.value = 'Good attempt! Try to use the word more naturally.'
    } else {
      feedback.value = 'Make sure to use the word in your sentence.'
    }
    
    submitted.value = true
  } catch (error) {
    console.error('Failed to score sentence:', error)
    // Default to medium score on error
    score.value = 0.5
    submitted.value = true
  } finally {
    scoring.value = false
  }
}

const handleNext = () => {
  // Quality based on score: 5 for high, 4 for medium, 3 for low
  let quality = 3
  if (score.value >= 0.7) quality = 5
  else if (score.value >= 0.4) quality = 4
  
  emit('complete', quality)
}

// Auto-speak on mount
onMounted(() => {
  speak(`Use ${props.word.word} in a sentence about your day`)
})
</script>

