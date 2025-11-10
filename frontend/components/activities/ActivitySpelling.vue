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
          <UInput
            v-model="userInput"
            placeholder="Type the word here..."
            size="xl"
            :disabled="answered"
            @keyup.enter="checkSpelling"
            class="text-center text-2xl"
          />
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

const userInput = ref('')
const answered = ref(false)
const isPlaying = ref(false)

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

