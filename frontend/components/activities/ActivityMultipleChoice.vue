<template>
  <div class="space-y-6">
    <h2 class="text-xl font-semibold text-center">Meaning Multiple Choice</h2>
    
    <UCard>
      <div class="space-y-6">
        <div class="text-center">
          <p class="text-2xl font-bold mb-2">{{ word.word }}</p>
          <p class="text-gray-600">Tap the meaning of <strong>{{ word.word }}</strong></p>
        </div>

        <div class="grid grid-cols-1 gap-3">
          <UButton
            v-for="(option, index) in options"
            :key="index"
            :color="selectedIndex === index ? (selectedIndex === correctIndex ? 'green' : 'red') : 'gray'"
            variant="outline"
            size="xl"
            block
            @click="selectOption(index)"
            :disabled="answered"
          >
            {{ option }}
          </UButton>
        </div>

        <div v-if="answered" class="text-center">
          <UButton
            @click="handleNext"
            color="primary"
            size="lg"
          >
            Continue
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

// Generate multiple choice options
const options = computed(() => {
  const correct = props.word.definition
  const distractors = [
    'A feeling of happiness',
    'Something that is difficult',
    'A type of animal',
    'To move quickly',
    'A place to live'
  ]
  
  // Shuffle and select 3 distractors
  const shuffled = [...distractors].sort(() => Math.random() - 0.5)
  const selected = [correct, ...shuffled.slice(0, 3)]
  
  // Shuffle options
  return selected.sort(() => Math.random() - 0.5)
})

const correctIndex = computed(() => {
  return options.value.findIndex(opt => opt === props.word.definition)
})

const selectedIndex = ref<number | null>(null)
const answered = ref(false)

const selectOption = (index: number) => {
  if (answered.value) return
  
  selectedIndex.value = index
  answered.value = true
  
  // Speak the word
  speak(`Tap the meaning of ${props.word.word}`)
}

const handleNext = () => {
  // Quality based on correctness
  const quality = selectedIndex.value === correctIndex.value ? 5 : 2
  emit('complete', quality)
}

// Auto-speak on mount
onMounted(() => {
  speak(`Tap the meaning of ${props.word.word}`)
})
</script>

