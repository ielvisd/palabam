<template>
  <div class="space-y-6">
    <h2 class="text-xl font-semibold text-center">Synonym/Antonym Selection</h2>
    
    <UCard>
      <div class="space-y-6">
        <div class="text-center">
          <p class="text-2xl font-bold mb-2">{{ word.word }}</p>
          <p class="text-gray-600">Is each word the same or opposite meaning?</p>
        </div>

        <div class="grid grid-cols-2 gap-3">
          <UButton
            v-for="(option, index) in options"
            :key="index"
            :color="selectedIndex === index ? (isCorrectSelection(index) ? 'green' : 'red') : 'gray'"
            variant="outline"
            size="xl"
            @click="selectOption(index)"
            :disabled="answered"
          >
            <div class="text-center">
              <div class="font-semibold">{{ option.word }}</div>
              <div class="text-xs mt-1">
                <UBadge :color="option.type === 'synonym' ? 'green' : 'red'" variant="soft" size="xs">
                  {{ option.type === 'synonym' ? 'Same' : 'Opposite' }}
                </UBadge>
              </div>
            </div>
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

// Generate synonym/antonym options
const options = computed(() => {
  // This would ideally come from a thesaurus API
  // For now, use sample data
  const synonyms = ['similar', 'alike', 'equivalent']
  const antonyms = ['different', 'opposite', 'contrary']
  
  // Mix synonyms and antonyms
  const mixed = [
    { word: synonyms[0], type: 'synonym' },
    { word: antonyms[0], type: 'antonym' },
    { word: synonyms[1], type: 'synonym' },
    { word: antonyms[1], type: 'antonym' }
  ]
  
  return mixed.sort(() => Math.random() - 0.5)
})

const selectedIndex = ref<number | null>(null)
const answered = ref(false)

const isCorrectSelection = (index: number) => {
  const option = options.value[index]
  // For this activity, we're checking if they correctly identified synonym/antonym
  // This is simplified - in production, would check against actual thesaurus data
  return option.type === 'synonym'
}

const selectOption = (index: number) => {
  if (answered.value) return
  
  selectedIndex.value = index
  answered.value = true
  
  speak(`Is ${options.value[index].word} the same or opposite meaning?`)
}

const handleNext = () => {
  // Quality based on correctness
  const quality = isCorrectSelection(selectedIndex.value!) ? 5 : 3
  emit('complete', quality)
}

// Auto-speak on mount
onMounted(() => {
  speak(`Is each word the same or opposite meaning of ${props.word.word}?`)
})
</script>

