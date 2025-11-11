<template>
  <UContainer class="py-8 max-w-4xl">
    <!-- Header -->
    <div class="mb-8">
      <h1 class="text-4xl font-bold mb-2 text-gray-900 dark:text-white">Upload Student Work</h1>
      <p class="text-gray-600 dark:text-gray-400 text-lg">
        Analyze student writing samples or transcripts to generate personalized vocabulary recommendations
      </p>
    </div>

    <UCard class="shadow-lg">
      <template #header>
        <div class="flex items-center justify-between">
          <h2 class="text-2xl font-semibold text-gray-900 dark:text-white">Upload & Analyze</h2>
        </div>
      </template>

      <UAlert
        v-if="error"
        color="error"
        variant="soft"
        :title="error"
        class="mb-6"
        @close="error = null"
      />

      <UAlert
        v-if="successMessage"
        color="success"
        variant="soft"
        :title="successMessage"
        class="mb-6"
      />

      <UForm :state="form" class="space-y-8" @submit="handleSubmit">
        <!-- Class and Student Selection -->
        <!-- 
          Student selection pattern: Hierarchical Class → Student
          This page uses hierarchical selection (vs. flat list on Story Spark page)
          because uploads are typically done in a structured workflow where teachers
          are working within a specific class context. This helps organize assessments
          by class and is better for bulk operations.
          
          Note: Submissions are stored with student_id only (no class_id). If a student
          is in multiple classes, their submissions are visible across all classes they're in.
        -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <UFormField label="Class" name="classId" required>
            <USelectMenu
              v-model="form.classId"
              :items="classes"
              value-key="id"
              label-key="name"
              placeholder="Select a class"
              :loading="loadingClasses"
              :disabled="loading || loadingClasses"
              size="lg"
              @update:model-value="onClassChange"
            />
          </UFormField>

          <UFormField label="Student" name="studentId" required>
            <USelectMenu
              v-model="form.studentId"
              :items="students"
              value-key="id"
              label-key="name"
              placeholder="Select a student"
              :disabled="!form.classId || loading || loadingStudents"
              :loading="loadingStudents"
              size="lg"
            />
          </UFormField>
        </div>

        <!-- Input Type Toggle -->
        <UFormField label="Input Type" name="inputType" required>
          <div class="flex gap-2">
            <UButton
              :color="inputType === 'writing' ? 'primary' : 'gray'"
              :variant="inputType === 'writing' ? 'solid' : 'outline'"
              size="lg"
              class="flex-1 border-2"
              :class="inputType === 'writing' ? 'border-primary' : 'border-gray-300 dark:border-gray-600'"
              @click="inputType = 'writing'"
            >
              <UIcon name="i-heroicons-document-text" class="mr-2" />
              Writing Sample
            </UButton>
            <UButton
              :color="inputType === 'transcript' ? 'primary' : 'gray'"
              :variant="inputType === 'transcript' ? 'solid' : 'outline'"
              size="lg"
              class="flex-1 border-2"
              :class="inputType === 'transcript' ? 'border-primary' : 'border-gray-300 dark:border-gray-600'"
              @click="inputType = 'transcript'"
            >
              <UIcon name="i-heroicons-microphone" class="mr-2" />
              Transcript
            </UButton>
          </div>
          <template #help>
            <span v-if="inputType === 'writing'">
              Single student writing sample. No speaker detection needed.
            </span>
            <span v-else>
              Multi-speaker transcript. System will detect and let you select the student speaker.
            </span>
          </template>
        </UFormField>

        <!-- File Upload or Text Input -->
        <UFormField 
          :label="inputType === 'writing' ? 'Writing Sample' : 'Transcript'" 
          name="content" 
          required
        >
          <!-- Combined File Upload and Text Input -->
          <div v-if="!uploadedFile" class="relative">
            <!-- Drag and Drop Zone with Text Input -->
            <div
              @drop.prevent="handleFileDrop"
              @dragover.prevent="handleDragOver"
              @dragenter.prevent="handleDragEnter"
              @dragleave.prevent="handleDragLeave"
              @dragend.prevent="handleDragEnd"
              :class="[
                'border-2 border-dashed rounded-lg transition-colors relative min-h-[500px]',
                isDragging 
                  ? 'border-primary bg-primary/5' 
                  : 'border-gray-300 dark:border-gray-700 hover:border-primary/50'
              ]"
            >
              <!-- Text Input Area -->
              <div class="p-6">
                <ClientOnly>
                  <UTextarea
                    v-model="form.transcript"
                    :placeholder="inputType === 'writing' 
                      ? 'Paste or type the student writing sample here, or drag and drop a file...' 
                      : 'Paste or type the transcript here, or drag and drop a file...'"
                    :rows="16"
                    :disabled="loading || extractingText"
                    autoresize
                    :maxrows="30"
                    size="lg"
                    class="resize-none min-h-[400px] text-base w-full"
                  />
                  <template #fallback>
                    <textarea
                      :placeholder="inputType === 'writing' 
                        ? 'Paste or type the student writing sample here, or drag and drop a file...' 
                        : 'Paste or type the transcript here, or drag and drop a file...'"
                      :rows="16"
                      :disabled="loading || extractingText"
                      class="resize-none min-h-[400px] text-base w-full rounded-md border-0 appearance-none placeholder:text-gray-600 focus:outline-none disabled:cursor-not-allowed disabled:opacity-75 transition-colors px-3 py-2 text-sm gap-2 text-highlighted bg-default ring ring-inset ring-accented resize-none focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-primary"
                    />
                  </template>
                </ClientOnly>
              </div>
              
              <!-- File Upload Overlay/Button -->
              <div class="absolute bottom-4 right-4 flex items-center gap-2">
                <UButton
                  variant="outline"
                  color="primary"
                  size="md"
                  @click.stop="fileInput?.click()"
                  :disabled="loading || extractingText"
                  class="bg-white dark:bg-gray-800 shadow-sm"
                >
                  <UIcon name="i-heroicons-folder-open" class="mr-2 w-5 h-5" />
                  Upload File
                </UButton>
                <input
                  ref="fileInput"
                  type="file"
                  accept=".txt,.md,.pdf,.docx"
                  class="hidden"
                  @change="handleFileSelect"
                />
              </div>
              
              <!-- Drag Overlay -->
              <div
                v-if="isDragging"
                class="absolute inset-0 bg-primary/10 border-2 border-primary border-dashed rounded-lg flex items-center justify-center z-10"
              >
                <div class="text-center">
                  <UIcon 
                    name="i-heroicons-cloud-arrow-up" 
                    class="w-16 h-16 mx-auto mb-4 text-primary"
                  />
                  <p class="text-lg font-medium text-primary">
                    Drop file here
                  </p>
                  <p class="text-sm text-gray-600 dark:text-gray-400 mt-2">
                    Supported: .txt, .md, .pdf, .docx
                  </p>
                </div>
              </div>
            </div>
          </div>

          <!-- Uploaded File Display -->
          <div v-else class="space-y-4">
            <UCard class="bg-gray-50 dark:bg-gray-800">
              <div class="flex items-center justify-between">
                <div class="flex items-center gap-3">
                  <UIcon name="i-heroicons-document" class="w-8 h-8 text-primary" />
                  <div>
                    <p class="font-medium text-gray-900 dark:text-white">{{ uploadedFile.name }}</p>
                    <p class="text-sm text-gray-500">
                      {{ formatFileSize(uploadedFile.size) }} • {{ extractedWordCount }} words
                    </p>
                  </div>
                </div>
                <UButton
                  variant="ghost"
                  color="red"
                  size="sm"
                  @click="removeFile"
                  :disabled="loading || extractingText"
                >
                  <UIcon name="i-heroicons-x-mark" class="w-5 h-5" />
                </UButton>
              </div>
            </UCard>

            <!-- Extracted Text Preview -->
            <div v-if="extractedText" class="space-y-2">
              <label class="text-sm font-medium text-gray-700 dark:text-gray-300">
                Extracted Text Preview
              </label>
              <UTextarea
                v-model="extractedText"
                :rows="8"
                :disabled="loading"
                autoresize
                :maxrows="15"
                size="lg"
                class="font-mono text-sm"
              />
            </div>
          </div>

          <template #help>
            <div class="flex items-center justify-between">
              <span>
                Minimum 25 words required. 
                <span v-if="wordCount > 0" :class="wordCount >= 25 ? 'text-success' : 'text-warning'">
                  {{ wordCount }} words
                </span>
              </span>
              <span v-if="extractingText" class="text-primary">
                <UIcon name="i-heroicons-arrow-path" class="w-4 h-4 inline animate-spin mr-1" />
                Extracting text...
              </span>
            </div>
          </template>
        </UFormField>

        <!-- Speaker Detection (Transcript Mode Only) -->
        <div v-if="inputType === 'transcript' && detectedSpeakers.length > 0" class="space-y-4">
          <UFormField label="Select Student Speaker" name="selectedSpeaker" required>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <UCard
                v-for="(speaker, idx) in detectedSpeakers"
                :key="idx"
                :class="[
                  'cursor-pointer transition-all hover:shadow-md',
                  selectedSpeaker === speaker.name 
                    ? 'ring-2 ring-primary bg-primary/5' 
                    : 'hover:bg-gray-50 dark:hover:bg-gray-800'
                ]"
                @click="selectedSpeaker = speaker.name"
              >
                <div class="space-y-3">
                  <div class="flex items-center justify-between">
                    <div class="flex items-center gap-2">
                      <input
                        type="radio"
                        :id="`speaker-${idx}`"
                        :value="speaker.name"
                        v-model="selectedSpeaker"
                        class="w-4 h-4 text-primary"
                      />
                      <label 
                        :for="`speaker-${idx}`" 
                        class="font-semibold text-lg text-gray-900 dark:text-white cursor-pointer"
                      >
                        {{ speaker.name }}
                      </label>
                    </div>
                    <UBadge color="primary" variant="soft">
                      {{ speaker.word_count }} words
                    </UBadge>
                  </div>
                  <p class="text-sm text-gray-600 dark:text-gray-400 italic line-clamp-2">
                    "{{ speaker.preview }}"
                  </p>
                  <div v-if="editingSpeaker === idx" class="flex gap-2">
                    <UInput
                      v-model="speaker.name"
                      size="sm"
                      placeholder="Speaker name"
                      @keyup.enter="editingSpeaker = null"
                    />
                    <UButton
                      size="xs"
                      color="primary"
                      @click="editingSpeaker = null"
                    >
                      Save
                    </UButton>
                  </div>
                  <UButton
                    v-else
                    variant="ghost"
                    size="xs"
                    @click.stop="editingSpeaker = idx"
                  >
                    <UIcon name="i-heroicons-pencil" class="w-4 h-4 mr-1" />
                    Edit name
                  </UButton>
                </div>
              </UCard>
            </div>
          </UFormField>
        </div>

        <!-- Auto-detect Speakers Button (Transcript Mode) -->
        <div v-if="inputType === 'transcript' && !detectedSpeakers.length && (form.transcript || extractedText)">
          <UButton
            variant="outline"
            color="primary"
            size="lg"
            :loading="detectingSpeakers"
            :disabled="!hasContentForDetection"
            @click="detectSpeakers"
            block
          >
            <UIcon name="i-heroicons-user-group" class="mr-2" />
            Detect Speakers
          </UButton>
        </div>

        <!-- Submit Button -->
        <div class="flex items-center justify-between pt-4 border-t border-gray-200 dark:border-gray-700">
          <div class="text-sm">
            <div v-if="wordCount > 0" :class="wordCount >= 25 ? 'text-success' : 'text-warning'">
              {{ wordCount }} words
            </div>
            <div v-else class="text-gray-400">No content yet</div>
            <div v-if="!canSubmit && validationMessage" class="text-warning text-xs mt-1">
              {{ validationMessage }}
            </div>
          </div>
          <UButton
            type="submit"
            :loading="loading"
            :disabled="!canSubmit"
            size="lg"
            color="primary"
          >
            <UIcon name="i-heroicons-magnifying-glass" class="mr-2" />
            Analyze {{ inputType === 'writing' ? 'Writing Sample' : 'Transcript' }}
          </UButton>
        </div>
      </UForm>

      <!-- Results -->
      <div v-if="result" class="mt-8 space-y-6">
        <UCard class="bg-success/10 border-success/30">
          <template #header>
            <div class="flex items-center gap-2">
              <UIcon name="i-heroicons-check-circle" class="text-success w-6 h-6" />
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
                        {{ getRelicTypeLabel(word.relic_type) }}
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

// Form state - use reactive for component-local state
// Reset on mount to prevent hydration mismatches
const form = reactive({
  classId: '',
  studentId: '',
  transcript: ''
})

// Input type toggle
const inputType = ref<'writing' | 'transcript'>('writing')

// File upload state
const fileInput = ref<HTMLInputElement | null>(null)
const uploadedFile = ref<File | null>(null)
const extractedText = ref<string>('')
const extractedWordCount = ref(0)
const extractingText = ref(false)
const isDragging = ref(false)

// Speaker detection state
const detectedSpeakers = ref<Array<{ name: string; text: string; word_count: number; preview: string }>>([])
const selectedSpeaker = ref<string>('')
const editingSpeaker = ref<number | null>(null)
const detectingSpeakers = ref(false)

// Loading and error states
const loading = ref(false)
const loadingClasses = ref(false)
const loadingStudents = ref(false)
const error = ref<string | null>(null)
const successMessage = ref<string | null>(null)
const result = ref<any>(null)

// Data
const classes = ref<Array<{ id: string; name: string }>>([])
const students = ref<Array<{ id: string; name: string }>>([])

// Computed
const classOptions = computed(() => {
  return classes.value.map(c => ({ label: c.name, value: c.id }))
})

const studentOptions = computed(() => {
  return students.value.map(s => ({ label: s.name, value: s.id }))
})

const wordCount = computed(() => {
  const content = extractedText.value || form.transcript
  return content.trim().split(/\s+/).filter(word => word.length > 0).length
})

const hasContentForDetection = computed(() => {
  return (form.transcript.trim().length > 0 || extractedText.value.trim().length > 0) && wordCount.value >= 25
})

const canSubmit = computed(() => {
  const hasContent = (extractedText.value || form.transcript).trim().length > 0
  const hasMinWords = wordCount.value >= 25
  const hasClassAndStudent = form.classId && form.studentId
  
  if (inputType.value === 'transcript') {
    return hasClassAndStudent && hasContent && hasMinWords && selectedSpeaker.value !== ''
  }
  
  return hasClassAndStudent && hasContent && hasMinWords
})

const validationMessage = computed(() => {
  if (canSubmit.value) return ''
  
  const hasContent = (extractedText.value || form.transcript).trim().length > 0
  const hasMinWords = wordCount.value >= 25
  const hasClass = !!form.classId
  const hasStudent = !!form.studentId
  
  if (!hasClass) {
    return 'Please select a class'
  }
  if (!hasStudent) {
    return 'Please select a student'
  }
  if (!hasContent) {
    return 'Please add content to analyze'
  }
  if (!hasMinWords) {
    return `Content must be at least 25 words (currently ${wordCount.value})`
  }
  if (inputType.value === 'transcript' && !selectedSpeaker.value) {
    return 'Please select a student speaker'
  }
  
  return ''
})

// File handling
const handleFileSelect = async (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (file) {
    await processFile(file)
  }
}

const handleDragOver = (event: DragEvent) => {
  event.preventDefault()
  event.stopPropagation()
  if (!isDragging.value) {
    isDragging.value = true
  }
}

const handleDragEnter = (event: DragEvent) => {
  event.preventDefault()
  event.stopPropagation()
  isDragging.value = true
}

const handleDragLeave = (event: DragEvent) => {
  event.preventDefault()
  event.stopPropagation()
  // Only set to false if we're leaving the drop zone (not just moving to a child element)
  const rect = (event.currentTarget as HTMLElement)?.getBoundingClientRect()
  if (rect) {
    const x = event.clientX
    const y = event.clientY
    if (x < rect.left || x > rect.right || y < rect.top || y > rect.bottom) {
      isDragging.value = false
    }
  }
}

const handleDragEnd = (event: DragEvent) => {
  event.preventDefault()
  event.stopPropagation()
  isDragging.value = false
}

const handleFileDrop = async (event: DragEvent) => {
  event.preventDefault()
  event.stopPropagation()
  isDragging.value = false
  
  const files = event.dataTransfer?.files
  if (files && files.length > 0) {
    const file = files[0]
    await processFile(file)
  }
}

const processFile = async (file: File) => {
  // Validate file type
  const allowedExtensions = ['.txt', '.md', '.pdf', '.docx']
  const fileExtension = '.' + file.name.split('.').pop()?.toLowerCase()
  
  if (!allowedExtensions.includes(fileExtension)) {
    error.value = `Unsupported file type. Supported types: ${allowedExtensions.join(', ')}`
    return
  }

  uploadedFile.value = file
  extractingText.value = true
  error.value = null

  try {
    const formData = new FormData()
    formData.append('file', file)

    const response = await $fetch(`${apiUrl}/api/submissions/extract-text`, {
      method: 'POST',
      body: formData
    }) as any

    extractedText.value = response.text
    extractedWordCount.value = response.word_count

    // Auto-detect speakers if in transcript mode
    if (inputType.value === 'transcript' && extractedText.value) {
      await detectSpeakers()
    }
  } catch (err: any) {
    console.error('Error extracting text:', err)
    error.value = err.data?.detail || err.message || 'Failed to extract text from file. Please try again.'
    uploadedFile.value = null
    extractedText.value = ''
  } finally {
    extractingText.value = false
  }
}

const removeFile = () => {
  uploadedFile.value = null
  extractedText.value = ''
  extractedWordCount.value = 0
  detectedSpeakers.value = []
  selectedSpeaker.value = ''
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

// Speaker detection
const detectSpeakers = async () => {
  const content = extractedText.value || form.transcript
  if (!content.trim() || wordCount.value < 25) {
    error.value = 'Content must be at least 25 words to detect speakers'
    return
  }

  detectingSpeakers.value = true
  error.value = null

  try {
    const response = await $fetch(`${apiUrl}/api/submissions/detect-speakers`, {
      method: 'POST',
      body: {
        transcript: content
      }
    }) as any

    detectedSpeakers.value = response.speakers || []
    
    // Auto-select first speaker if only one detected
    if (detectedSpeakers.value.length === 1) {
      selectedSpeaker.value = detectedSpeakers.value[0].name
    } else if (detectedSpeakers.value.length > 1) {
      // Try to auto-select based on student name
      const studentName = students.value.find(s => s.id === form.studentId)?.name
      if (studentName) {
        const matchingSpeaker = detectedSpeakers.value.find(s => 
          s.name.toLowerCase().includes(studentName.toLowerCase()) ||
          studentName.toLowerCase().includes(s.name.toLowerCase())
        )
        if (matchingSpeaker) {
          selectedSpeaker.value = matchingSpeaker.name
        }
      }
    }
  } catch (err: any) {
    console.error('Error detecting speakers:', err)
    error.value = err.data?.detail || err.message || 'Failed to detect speakers. Please try again.'
  } finally {
    detectingSpeakers.value = false
  }
}

// Watch for content changes in transcript mode
watch([() => form.transcript, () => extractedText, () => inputType], () => {
  if (inputType.value === 'transcript' && (form.transcript || extractedText.value)) {
    // Reset speaker detection when content changes
    detectedSpeakers.value = []
    selectedSpeaker.value = ''
  }
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

// Submit for analysis
// Note: Submissions are stored with student_id only (no class_id)
// This means if a student is in multiple classes, their submissions are visible
// across all classes. Vocabulary analysis is shared across all classes (Option A).
const handleSubmit = async () => {
  if (!canSubmit.value) return

  loading.value = true
  error.value = null
  successMessage.value = null
  result.value = null

  try {
    const content = extractedText.value || form.transcript
    
    // Use submissions endpoint for better control
    // Submissions are student-scoped: only student_id is stored, not class_id
    const response = await $fetch(`${apiUrl}/api/submissions/`, {
      method: 'POST',
      body: {
        student_id: form.studentId,
        type: inputType.value === 'writing' ? 'teacher-upload' : 'teacher-upload',
        content: content,
        source: uploadedFile.value ? 'file' : 'text',
        student_speaker_name: inputType.value === 'transcript' ? selectedSpeaker.value : null
      }
    }) as any

    result.value = response
    successMessage.value = `${inputType.value === 'writing' ? 'Writing sample' : 'Transcript'} analyzed successfully! Recommendations have been generated.`
  } catch (err: any) {
    console.error('Error analyzing:', err)
    error.value = err.data?.detail || err.message || `Failed to analyze ${inputType.value}. Please try again.`
  } finally {
    loading.value = false
  }
}

const resetForm = () => {
  form.transcript = ''
  extractedText.value = ''
  uploadedFile.value = null
  detectedSpeakers.value = []
  selectedSpeaker.value = ''
  result.value = null
  error.value = null
  successMessage.value = null
  if (fileInput.value) {
    fileInput.value.value = ''
  }
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

const getRelicTypeLabel = (type?: string) => {
  const labels: Record<string, string> = {
    whisper: 'Easy',
    echo: 'Basic',
    resonance: 'Intermediate',
    thunder: 'Advanced'
  }
  return labels[type || ''] || 'Basic'
}

onMounted(() => {
  // Reset form state on mount to ensure clean state
  form.transcript = ''
  form.classId = ''
  form.studentId = ''
  extractedText.value = ''
  detectedSpeakers.value = []
  selectedSpeaker.value = ''
  fetchClasses()
})

useHead({
  title: 'Upload Student Work - Palabam'
})
</script>
