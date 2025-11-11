<template>
  <UContainer class="py-8">
    <div class="mb-6">
      <h1 class="text-4xl font-bold mb-2">Upload Transcript</h1>
      <p class="text-gray-600 dark:text-gray-400">Analyze a student transcript to generate vocabulary recommendations</p>
    </div>

    <UCard>
      <UAlert
        v-if="error"
        color="error"
        variant="soft"
        :title="error"
        class="mb-4"
        @close="error = null"
      />

      <UAlert
        v-if="successMessage"
        color="success"
        variant="soft"
        :title="successMessage"
        class="mb-4"
      />

      <UForm :state="form" class="space-y-6" @submit="handleSubmit">
        <UFormField label="Class" name="classId" required>
          <USelect
            v-model="form.classId"
            :options="classOptions"
            placeholder="Select a class"
            :loading="loadingClasses"
            :disabled="loading || loadingClasses"
            @update:model-value="onClassChange"
          />
        </UFormField>

        <UFormField label="Student" name="studentId" required>
          <USelect
            v-model="form.studentId"
            :options="studentOptions"
            placeholder="Select a student"
            :disabled="!form.classId || loading || loadingStudents"
            :loading="loadingStudents"
          />
        </UFormField>

        <UFormField label="Transcript" name="transcript" required>
          <UTextarea
            v-model="form.transcript"
            placeholder="Paste or type the student transcript here..."
            :rows="10"
            :disabled="loading"
            autoresize
            :maxrows="20"
          />
          <template #help>
            Minimum 10 words required. The transcript will be analyzed to generate vocabulary recommendations.
          </template>
        </UFormField>

        <div class="flex items-center justify-between">
          <p class="text-sm text-gray-600 dark:text-gray-400">
            {{ wordCount }} words
          </p>
          <UButton
            type="submit"
            :loading="loading"
            :disabled="!canSubmit"
            size="lg"
          >
            Analyze Transcript
          </UButton>
        </div>
      </UForm>

      <!-- Results -->
      <div v-if="result" class="mt-8 space-y-6">
        <UCard class="bg-success/10 border-success/30">
          <template #header>
            <div class="flex items-center gap-2">
              <UIcon name="i-heroicons-check-circle" class="text-success" />
              <h2 class="text-xl font-bold">Analysis Complete!</h2>
            </div>
          </template>

          <div class="space-y-4">
            <div>
              <h3 class="font-semibold mb-2">Vocabulary Level</h3>
              <UBadge
                :color="getLevelColor(result.vocabulary_level)"
                size="lg"
                variant="soft"
              >
                {{ result.vocabulary_level }}
              </UBadge>
            </div>

            <div v-if="result.recommended_words && result.recommended_words.length > 0">
              <h3 class="font-semibold mb-3">Recommended Words ({{ result.recommended_words.length }})</h3>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <UCard
                  v-for="(word, idx) in result.recommended_words"
                  :key="idx"
                  class="p-4"
                >
                  <div class="space-y-2">
                    <div class="flex items-center justify-between">
                      <span class="font-bold text-lg">
                        {{ typeof word === 'string' ? word : word.word }}
                      </span>
                      <UBadge
                        v-if="typeof word !== 'string' && word.relic_type"
                        :color="getRelicTypeColor(word.relic_type)"
                        variant="soft"
                        size="sm"
                      >
                        {{ word.relic_type }}
                      </UBadge>
                    </div>
                    <p v-if="typeof word !== 'string' && word.definition" class="text-sm text-gray-700 dark:text-gray-300">
                      {{ word.definition }}
                    </p>
                    <p v-if="typeof word !== 'string' && word.example" class="text-sm text-gray-600 dark:text-gray-400 italic">
                      "{{ word.example }}"
                    </p>
                    <div v-if="typeof word !== 'string' && word.difficulty_score" class="text-xs text-gray-500">
                      Difficulty: {{ word.difficulty_score }}/100
                    </div>
                  </div>
                </UCard>
              </div>
            </div>

            <div class="flex gap-4 pt-4">
              <UButton
                :to="`/students/${form.studentId}`"
                color="primary"
                size="lg"
                block
              >
                View Student Details
              </UButton>
              <UButton
                @click="resetForm"
                variant="outline"
                color="neutral"
                size="lg"
                block
              >
                Analyze Another
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
  middleware: 'auth'
})

const { getTeacherId } = useAuth()
const config = useRuntimeConfig()
const apiUrl = config.public.apiUrl || 'http://localhost:8000'
const router = useRouter()

const form = reactive({
  classId: '',
  studentId: '',
  transcript: ''
})

const loading = ref(false)
const loadingClasses = ref(false)
const loadingStudents = ref(false)
const error = ref<string | null>(null)
const successMessage = ref<string | null>(null)
const result = ref<any>(null)

const classes = ref<Array<{ id: string; name: string }>>([])
const students = ref<Array<{ id: string; name: string }>>([])

const classOptions = computed(() => {
  return classes.value.map(c => ({ label: c.name, value: c.id }))
})

const studentOptions = computed(() => {
  return students.value.map(s => ({ label: s.name, value: s.id }))
})

const wordCount = computed(() => {
  return form.transcript.trim().split(/\s+/).filter(word => word.length > 0).length
})

const canSubmit = computed(() => {
  return form.classId && form.studentId && form.transcript.trim().length >= 10 && wordCount.value >= 10
})

// Fetch teacher's classes
const fetchClasses = async () => {
  loadingClasses.value = true
  try {
    const teacherId = await getTeacherId()
    if (!teacherId) {
      throw new Error('Teacher not found')
    }
    const response = await $fetch(`${apiUrl}/api/classes/teacher/${teacherId}`) as any
    classes.value = response.classes || []
  } catch (err: any) {
    console.error('Error fetching classes:', err)
    error.value = 'Failed to load classes. Please try again.'
  } finally {
    loadingClasses.value = false
  }
}

// Fetch students for selected class
const onClassChange = async (classId: string) => {
  if (!classId) {
    students.value = []
    form.studentId = ''
    return
  }

  loadingStudents.value = true
  try {
    const response = await $fetch(`${apiUrl}/api/students/class/${classId}`) as any
    students.value = response.students || []
    form.studentId = ''
  } catch (err: any) {
    console.error('Error fetching students:', err)
    error.value = 'Failed to load students. Please try again.'
  } finally {
    loadingStudents.value = false
  }
}

// Submit transcript for analysis
const handleSubmit = async () => {
  if (!canSubmit.value) return

  loading.value = true
  error.value = null
  successMessage.value = null
  result.value = null

  try {
    const response = await $fetch(`${apiUrl}/api/profile/`, {
      method: 'POST',
      body: {
        transcript: form.transcript,
        student_id: form.studentId,
        inputMode: 'text'
      }
    }) as any

    result.value = response
    successMessage.value = 'Transcript analyzed successfully! Recommendations have been generated.'
    
    // Redirect to student detail page after a short delay
    setTimeout(() => {
      router.push(`/students/${form.studentId}`)
    }, 3000)
  } catch (err: any) {
    console.error('Error analyzing transcript:', err)
    error.value = err.data?.detail || err.message || 'Failed to analyze transcript. Please try again.'
  } finally {
    loading.value = false
  }
}

const resetForm = () => {
  form.transcript = ''
  result.value = null
  error.value = null
  successMessage.value = null
}

const getLevelColor = (level?: string) => {
  const colors: Record<string, string> = {
    'K-1': 'primary',
    '2-3': 'primary',
    '4-5': 'teal',
    '6-7': 'teal',
    '8-9': 'yellow',
    '10-11': 'yellow',
    '12+': 'pink',
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

onMounted(() => {
  fetchClasses()
})

useHead({
  title: 'Upload Transcript - Palabam'
})
</script>
