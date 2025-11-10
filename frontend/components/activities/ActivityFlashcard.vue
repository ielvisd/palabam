<template>
  <div class="space-y-6">
    <h2 class="text-xl font-semibold text-center">Flashcard Introduction</h2>
    
    <UCard class="min-h-[300px] flex items-center justify-center">
      <div class="text-center space-y-4">
        <div class="text-4xl font-bold text-primary mb-4">
          {{ word.word }}
        </div>
        <div class="text-lg text-gray-700">
          {{ word.definition }}
        </div>
        <div v-if="word.example" class="text-sm text-gray-500 italic mt-4">
          "{{ word.example }}"
        </div>
      </div>
    </UCard>

    <div class="flex gap-4 justify-center">
      <UButton
        @click="playAudio"
        color="primary"
        variant="outline"
        :disabled="isPlaying"
      >
        <UIcon name="i-heroicons-speaker-wave" class="mr-2" />
        {{ isPlaying ? 'Playing...' : 'Hear Pronunciation' }}
      </UButton>
      <UButton
        @click="handleComplete"
        color="primary"
        size="lg"
      >
        I Understand
      </UButton>
    </div>
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
const isPlaying = ref(false)

const playAudio = () => {
  isPlaying.value = true
  speak(props.word.word)
  
  // Reset after speaking
  setTimeout(() => {
    isPlaying.value = false
  }, 2000)
}

const handleComplete = () => {
  // Quality 4 = correct response after hesitation (first time seeing word)
  emit('complete', 4)
}

// Auto-play on mount
onMounted(() => {
  playAudio()
})
</script>

