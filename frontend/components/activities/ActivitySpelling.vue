<template>
  <div class="space-y-6">
    <h2 class="text-xl font-semibold text-center">Dictated Spelling</h2>
    
    <UCard>
      <div class="space-y-6">
        <div class="text-center">
          <p class="text-gray-600 mb-4">Listen and spell the word</p>
          <UButton
            @click="playWord"
            color="primary"
            variant="outline"
            :disabled="isPlaying"
          >
            <UIcon name="i-heroicons-speaker-wave" class="mr-2" />
            {{ isPlaying ? 'Playing...' : 'Hear Word Again' }}
          </UButton>
        </div>

        <div>
          <label class="block text-sm font-medium mb-2">Spell the word:</label>
          <div class="relative flex items-center gap-2">
            <UInput
              v-model="userInput"
              placeholder="Type the word here..."
              size="xl"
              :disabled="answered || isRecordingAudio"
              @keyup.enter="checkSpelling"
              class="text-center text-2xl flex-1"
            />
            <UButton
              v-if="!isRecordingAudio"
              @click="handleAudioInput"
              :disabled="answered"
              variant="ghost"
              color="primary"
              size="sm"
              :title="'Start voice input'"
            >
              <UIcon name="i-heroicons-microphone" class="w-5 h-5" />
            </UButton>
            <UButton
              v-else
              @click="stopAudioRecording"
              :disabled="answered"
              color="red"
              size="sm"
              :title="'Stop recording'"
            >
              <UIcon name="i-heroicons-stop-circle" class="w-5 h-5" />
            </UButton>
          </div>
        </div>
        <div v-if="isRecordingAudio" class="text-center">
          <div class="inline-flex items-center gap-2 text-red-600">
            <span class="animate-pulse">●</span>
            <span class="text-sm">Recording...</span>
          </div>
        </div>

        <div v-if="answered" class="text-center space-y-4">
          <div :class="isCorrect ? 'text-green-600' : 'text-red-600'">
            <p class="text-lg font-semibold">
              {{ isCorrect ? 'Correct!' : `Incorrect. The word is: ${word.word}` }}
            </p>
          </div>
          <UButton
            @click="handleNext"
            color="primary"
            size="lg"
          >
            Continue
          </UButton>
        </div>

        <div v-else class="text-center">
          <UButton
            @click="checkSpelling"
            color="primary"
            size="lg"
            :disabled="!userInput.trim()"
          >
            Check Spelling
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

const userInput = ref('')
const answered = ref(false)
const isPlaying = ref(false)

// Handle audio input
const handleAudioInput = () => {
  startAudioRecording()
}

// Watch for transcript updates and update userInput
watch(audioTranscript, (newTranscript) => {
  if (newTranscript && isRecordingAudio.value) {
    const transcriptText = newTranscript.trim()
    if (transcriptText) {
      // For spelling, replace the input with the transcript
      userInput.value = transcriptText
    }
  }
})

// Watch for recording to stop and finalize any remaining transcript
watch(isRecordingAudio, (recording) => {
  if (!recording) {
    const finalTranscript = getCurrentTranscript.value.trim()
    if (finalTranscript) {
      userInput.value = finalTranscript
    }
    clearAudioTranscript()
  }
})

const isCorrect = computed(() => {
  return userInput.value.toLowerCase().trim() === props.word.word.toLowerCase()
})

const playWord = () => {
  isPlaying.value = true
  speak(`Spell ${props.word.word}`)
  
  setTimeout(() => {
    isPlaying.value = false
  }, 2000)
}

const checkSpelling = () => {
  if (!userInput.value.trim()) return
  answered.value = true
}

const handleNext = () => {
  // Quality: 5 if correct, 1 if incorrect
  const quality = isCorrect.value ? 5 : 1
  emit('complete', quality)
}

// Auto-play on mount
onMounted(() => {
  playWord()
})
</script>

