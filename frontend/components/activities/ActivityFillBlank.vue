<template>
  <div class="space-y-6">
    <h2 class="text-xl font-semibold text-center">Context Fill-in-the-Blank</h2>
    
    <UCard>
      <div class="space-y-6">
        <div class="text-center">
          <p class="text-gray-600 mb-4">Complete the sentence</p>
          <UButton
            @click="playSentence"
            color="primary"
            variant="outline"
            :disabled="isPlaying"
          >
            <UIcon name="i-heroicons-speaker-wave" class="mr-2" />
            {{ isPlaying ? 'Playing...' : 'Hear Sentence' }}
          </UButton>
        </div>

        <div class="text-lg">
          <p class="text-center">
            {{ sentenceParts[0] }}
            <span class="inline-flex items-center gap-1">
              <UInput
                v-model="userInput"
                :placeholder="word.word"
                size="lg"
                :disabled="answered || isRecordingAudio"
                class="inline-block w-32 text-center"
                @keyup.enter="checkAnswer"
              />
              <UButton
                v-if="!isRecordingAudio"
                @click="handleAudioInput"
                :disabled="answered"
                variant="ghost"
                color="primary"
                size="xs"
                class="p-1"
                :title="'Start voice input'"
              >
                <UIcon name="i-heroicons-microphone" class="w-4 h-4" />
              </UButton>
              <UButton
                v-else
                @click="stopAudioRecording"
                :disabled="answered"
                color="red"
                size="xs"
                class="p-1"
                :title="'Stop recording'"
              >
                <UIcon name="i-heroicons-stop-circle" class="w-4 h-4" />
              </UButton>
            </span>
            {{ sentenceParts[1] }}
          </p>
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
              {{ isCorrect ? 'Correct!' : `Incorrect. The answer is: ${word.word}` }}
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
            @click="checkAnswer"
            color="primary"
            size="lg"
            :disabled="!userInput.trim()"
          >
            Check Answer
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
      // For fill-in-the-blank, replace the input with the transcript
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

// Generate sentence with blank
const sentence = computed(() => {
  if (props.word.example) {
    return props.word.example.replace(props.word.word, '___')
  }
  // Generate simple sentence
  return `The team was ___ after the loss.`
})

const sentenceParts = computed(() => {
  return sentence.value.split('___')
})

const isCorrect = computed(() => {
  return userInput.value.toLowerCase().trim() === props.word.word.toLowerCase()
})

const playSentence = () => {
  isPlaying.value = true
  const fullSentence = sentence.value.replace('___', props.word.word)
  speak(`Complete: ${fullSentence}`)
  
  setTimeout(() => {
    isPlaying.value = false
  }, 3000)
}

const checkAnswer = () => {
  if (!userInput.value.trim()) return
  answered.value = true
}

const handleNext = () => {
  // Quality: 5 if correct, 2 if incorrect
  const quality = isCorrect.value ? 5 : 2
  emit('complete', quality)
}

// Auto-play on mount
onMounted(() => {
  playSentence()
})
</script>

