<template>
  <UContainer class="py-8">
    <UCard>
      <template #header>
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-3xl font-bold">Educator Dashboard</h1>
            <p class="text-gray-600 mt-2">View vocabulary recommendations for your students</p>
          </div>
          <div class="flex gap-2">
            <UButton
              @click="showCreateClassModal = true"
              color="primary"
            >
              <UIcon name="i-heroicons-plus-circle" class="mr-2" />
              Create Class
            </UButton>
            <UButton
              @click="exportToCSV"
              variant="outline"
              :loading="exporting"
            >
              <UIcon name="i-heroicons-arrow-down-tray" class="mr-2" />
              Export CSV
            </UButton>
            <UButton
              @click="exportToPDF"
              variant="outline"
              :loading="exporting"
            >
              <UIcon name="i-heroicons-document-arrow-down" class="mr-2" />
              Export PDF
            </UButton>
          </div>
        </div>
      </template>

      <!-- Classes Section -->
      <div v-if="classes.length > 0" class="mb-8">
        <h2 class="text-2xl font-semibold mb-4">My Classes</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <UCard
            v-for="classItem in classes"
            :key="classItem.id"
            class="hover:shadow-lg transition-shadow"
          >
            <template #header>
              <div class="flex items-center justify-between">
                <h3 class="text-lg font-semibold">{{ classItem.name }}</h3>
                <UButton
                  @click="copyClassCode(classItem.code)"
                  variant="ghost"
                  size="sm"
                >
                  <UIcon name="i-heroicons-clipboard-document" />
                </UButton>
              </div>
            </template>
            
            <div class="space-y-3">
              <div>
                <label class="text-xs text-gray-500">Class Code</label>
                <div class="flex items-center gap-2 mt-1">
                  <code class="text-lg font-mono font-bold tracking-widest bg-gray-100 px-3 py-1 rounded">
                    {{ classItem.code }}
                  </code>
                  <UButton
                    @click="copyClassCode(classItem.code)"
                    variant="ghost"
                    size="xs"
                  >
                    Copy
                  </UButton>
                </div>
              </div>
              
              <div class="flex items-center justify-between text-sm">
                <span class="text-gray-600">
                  {{ classItem.student_count || 0 }} students
                </span>
                <UButton
                  @click="viewClassStudents(classItem.id)"
                  variant="ghost"
                  size="sm"
                >
                  View Students
                </UButton>
              </div>
              
              <div class="text-xs text-gray-500">
                Created {{ formatDate(classItem.created_at) }}
              </div>
            </div>
          </UCard>
        </div>
      </div>

      <!-- Create Class Modal -->
      <UModal v-model="showCreateClassModal">
        <UCard>
          <template #header>
            <h2 class="text-2xl font-bold">Create New Class</h2>
          </template>
          
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium mb-2">Class Name</label>
              <UInput
                v-model="newClassName"
                placeholder="e.g., 7th Grade ELA - Period 1"
                size="lg"
              />
            </div>
            
            <UAlert
              v-if="createClassError"
              color="red"
              variant="soft"
              :title="createClassError"
              @close="createClassError = null"
            />
            
            <div class="flex gap-4">
              <UButton
                @click="createClass"
                color="primary"
                :loading="creatingClass"
                :disabled="!newClassName.trim()"
                block
              >
                Create Class
              </UButton>
              <UButton
                @click="showCreateClassModal = false"
                variant="outline"
                block
              >
                Cancel
              </UButton>
            </div>
          </div>
        </UCard>
      </UModal>

      <!-- New Class Success Modal -->
      <UModal v-model="showClassCreatedModal">
        <UCard>
          <template #header>
            <div class="flex items-center gap-2">
              <UIcon name="i-heroicons-check-circle" class="text-green-600 text-2xl" />
              <h2 class="text-2xl font-bold">Class Created!</h2>
            </div>
          </template>
          
          <div class="space-y-4">
            <div>
              <p class="text-gray-600 mb-4">
                Share this code with your students so they can join:
              </p>
              <div class="flex items-center gap-2">
                <code class="text-3xl font-mono font-bold tracking-widest bg-gray-100 px-4 py-2 rounded flex-1 text-center">
                  {{ newClassCode }}
                </code>
                <UButton
                  @click="copyClassCode(newClassCode)"
                  color="primary"
                >
                  <UIcon name="i-heroicons-clipboard-document" class="mr-2" />
                  Copy
                </UButton>
              </div>
            </div>
            
            <UAlert color="blue" variant="soft">
              <p class="text-sm">
                Students can join by going to <strong>/join-class</strong> and entering this code.
              </p>
            </UAlert>
            
            <UButton
              @click="closeClassCreatedModal"
              color="primary"
              block
            >
              Done
            </UButton>
          </div>
        </UCard>
      </UModal>

      <!-- Search and Filter -->
      <div class="mb-6 space-y-4">
        <div class="flex gap-4">
          <UInput
            v-model="searchQuery"
            placeholder="Search students or words..."
            icon="i-heroicons-magnifying-glass"
            class="flex-1"
          />
          <USelect
            v-model="selectedLevel"
            :options="vocabularyLevels"
            placeholder="Filter by level"
            class="w-48"
          />
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="text-center py-12">
        <UIcon name="i-heroicons-arrow-path" class="animate-spin text-4xl mb-4" />
        <p class="text-gray-600">Loading student data...</p>
      </div>

      <!-- Students List -->
      <div v-else-if="filteredStudents.length > 0" class="space-y-4">
        <UCard
          v-for="student in filteredStudents"
          :key="student.id"
          class="hover:shadow-lg transition-shadow"
        >
          <template #header>
            <div class="flex items-center justify-between">
              <div>
                <h2 class="text-xl font-semibold">{{ student.name }}</h2>
                <div class="flex items-center gap-4 mt-2">
                  <UBadge
                    :color="getLevelColor(student.vocabulary_level)"
                    variant="soft"
                  >
                    {{ student.vocabulary_level || 'Not assessed' }}
                  </UBadge>
                  <span class="text-sm text-gray-600">
                    Last profile: {{ formatDate(student.last_profile_date) }}
                  </span>
                </div>
              </div>
              <UButton
                @click="toggleStudent(student.id)"
                variant="ghost"
                size="sm"
              >
                <UIcon
                  :name="expandedStudents.has(student.id) ? 'i-heroicons-chevron-up' : 'i-heroicons-chevron-down'"
                />
              </UButton>
            </div>
          </template>

          <!-- Recommended Words -->
          <div v-if="expandedStudents.has(student.id)" class="space-y-4">
            <div v-if="student.recommended_words && student.recommended_words.length > 0">
              <h3 class="font-semibold mb-3">Recommended Words ({{ student.recommended_words.length }})</h3>
              <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                <UCard
                  v-for="word in student.recommended_words"
                  :key="word.word || word"
                  class="p-4"
                >
                  <div class="space-y-2">
                    <div class="flex items-center justify-between">
                      <span class="font-semibold text-lg">
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
                    <p v-if="typeof word !== 'string' && word.definition" class="text-sm text-gray-600">
                      {{ word.definition }}
                    </p>
                    <p v-if="typeof word !== 'string' && word.example" class="text-sm text-gray-500 italic">
                      "{{ word.example }}"
                    </p>
                    <div v-if="typeof word !== 'string' && word.difficulty_score" class="text-xs text-gray-500">
                      Difficulty: {{ word.difficulty_score }}/100
                    </div>
                  </div>
                </UCard>
              </div>
            </div>
            <div v-else class="text-center py-8 text-gray-500">
              <p>No recommendations yet. Upload a transcript to generate recommendations.</p>
              <UButton
                to="/spark"
                variant="outline"
                class="mt-4"
              >
                Analyze Transcript
              </UButton>
            </div>

            <!-- Profile History -->
            <div v-if="student.profiles && student.profiles.length > 0" class="mt-6">
              <h3 class="font-semibold mb-3">Profile History</h3>
              <div class="space-y-2">
                <UCard
                  v-for="profile in student.profiles"
                  :key="profile.id"
                  class="p-3"
                >
                  <div class="flex items-center justify-between">
                    <div>
                      <span class="text-sm font-medium">
                        {{ formatDate(profile.created_at) }}
                      </span>
                      <p class="text-xs text-gray-500 mt-1">
                        {{ profile.resonance_data?.unique_words || 0 }} unique words analyzed
                      </p>
                    </div>
                    <UButton
                      @click="viewProfile(profile.id)"
                      variant="ghost"
                      size="sm"
                    >
                      View Details
                    </UButton>
                  </div>
                </UCard>
              </div>
            </div>
          </div>
        </UCard>
      </div>

      <!-- Empty State -->
      <div v-else class="text-center py-12">
        <UIcon name="i-heroicons-user-group" class="text-6xl text-gray-400 mb-4" />
        <h3 class="text-xl font-semibold mb-2">No students found</h3>
        <p class="text-gray-600 mb-4">
          {{ searchQuery ? 'Try adjusting your search filters.' : 'Start by analyzing student transcripts.' }}
        </p>
        <UButton
          to="/spark"
          color="primary"
        >
          Analyze First Transcript
        </UButton>
      </div>
    </UCard>
  </UContainer>
</template>

<script setup lang="ts">
interface Student {
  id: string
  name: string
  vocabulary_level?: string
  recommended_words?: Array<string | {
    word: string
    definition?: string
    example?: string
    relic_type?: string
    difficulty_score?: number
  }>
  last_profile_date?: string
  profiles?: Array<{
    id: string
    created_at: string
    resonance_data?: {
      unique_words?: number
    }
  }>
}

const config = useRuntimeConfig()
const apiUrl = config.public.apiUrl || 'http://localhost:8000'

// State
const loading = ref(true)
const exporting = ref(false)
const searchQuery = ref('')
const selectedLevel = ref<string | null>(null)
const expandedStudents = ref(new Set<string>())
const students = ref<Student[]>([])
const classes = ref<any[]>([])
const showCreateClassModal = ref(false)
const showClassCreatedModal = ref(false)
const newClassName = ref('')
const newClassCode = ref('')
const creatingClass = ref(false)
const createClassError = ref<string | null>(null)

// Get teacher ID (in production, from auth)
const teacherId = useCookie('teacher_id').value || 'temp-teacher-id'

// Vocabulary levels for filtering
const vocabularyLevels = [
  { label: 'All Levels', value: null },
  { label: 'Beginner', value: 'beginner' },
  { label: 'Intermediate', value: 'intermediate' },
  { label: 'Advanced', value: 'advanced' },
  { label: 'Expert', value: 'expert' }
]

// Fetch classes
const fetchClasses = async () => {
  try {
    const response = await $fetch(`${apiUrl}/api/classes/teacher/${teacherId}`)
    classes.value = response.classes || []
    
    // Fetch student counts for each class
    for (const classItem of classes.value) {
      try {
        const studentsRes = await $fetch(`${apiUrl}/api/classes/${classItem.id}/students`)
        classItem.student_count = studentsRes.students?.length || 0
      } catch (e) {
        classItem.student_count = 0
      }
    }
  } catch (error) {
    console.error('Failed to fetch classes:', error)
    classes.value = []
  }
}

// Create new class
const createClass = async () => {
  if (!newClassName.value.trim()) return

  creatingClass.value = true
  createClassError.value = null

  try {
    const response = await $fetch(`${apiUrl}/api/classes/`, {
      method: 'POST',
      body: {
        teacher_id: teacherId,
        name: newClassName.value.trim()
      }
    })

    newClassCode.value = response.code
    showCreateClassModal.value = false
    showClassCreatedModal.value = true
    
    // Refresh classes list
    await fetchClasses()
    
    // Reset form
    newClassName.value = ''
  } catch (err: any) {
    createClassError.value = err.message || 'Failed to create class. Please try again.'
    console.error('Create class error:', err)
  } finally {
    creatingClass.value = false
  }
}

const closeClassCreatedModal = () => {
  showClassCreatedModal.value = false
  newClassCode.value = ''
}

const copyClassCode = async (code: string) => {
  try {
    await navigator.clipboard.writeText(code)
    // Could show a toast notification here
    alert(`Class code ${code} copied to clipboard!`)
  } catch (err) {
    // Fallback for older browsers
    const textarea = document.createElement('textarea')
    textarea.value = code
    document.body.appendChild(textarea)
    textarea.select()
    document.execCommand('copy')
    document.body.removeChild(textarea)
    alert(`Class code ${code} copied to clipboard!`)
  }
}

const viewClassStudents = async (classId: string) => {
  try {
    const response = await $fetch(`${apiUrl}/api/classes/${classId}/students`)
    // TODO: Show students in a modal or navigate to a class detail page
    alert(`This class has ${response.students?.length || 0} students enrolled.`)
  } catch (error) {
    console.error('Failed to fetch class students:', error)
  }
}

// Fetch students and their recommendations
const fetchStudents = async () => {
  loading.value = true
  try {
    // TODO: Replace with actual API call to get students
    // For now, using mock data structure
    // In production: const response = await $fetch(`${apiUrl}/api/students/`)
    
    // Mock data for demonstration
    students.value = [
      {
        id: '1',
        name: 'Alex Johnson',
        vocabulary_level: 'intermediate',
        recommended_words: [
          {
            word: 'resilient',
            definition: 'able to recover quickly from difficulties',
            example: 'She was resilient after the setback.',
            relic_type: 'resonance',
            difficulty_score: 65
          },
          {
            word: 'perseverance',
            definition: 'persistence in doing something despite difficulty',
            example: 'His perseverance paid off in the end.',
            relic_type: 'thunder',
            difficulty_score: 75
          },
          'determined',
          'accomplish',
          'discover'
        ],
        last_profile_date: new Date().toISOString(),
        profiles: [
          {
            id: 'p1',
            created_at: new Date().toISOString(),
            resonance_data: { unique_words: 45 }
          }
        ]
      },
      {
        id: '2',
        name: 'Sam Martinez',
        vocabulary_level: 'beginner',
        recommended_words: [
          {
            word: 'curious',
            definition: 'eager to know or learn something',
            example: 'The curious child asked many questions.',
            relic_type: 'echo',
            difficulty_score: 35
          },
          {
            word: 'adventure',
            definition: 'an exciting or dangerous experience',
            example: 'We went on an adventure in the forest.',
            relic_type: 'echo',
            difficulty_score: 40
          }
        ],
        last_profile_date: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
        profiles: []
      }
    ]
  } catch (error) {
    console.error('Failed to fetch students:', error)
  } finally {
    loading.value = false
  }
}

// Filtered students
const filteredStudents = computed(() => {
  let filtered = students.value

  // Search filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(student => {
      const nameMatch = student.name.toLowerCase().includes(query)
      const wordsMatch = student.recommended_words?.some(word => {
        const wordText = typeof word === 'string' ? word : word.word
        return wordText.toLowerCase().includes(query)
      })
      return nameMatch || wordsMatch
    })
  }

  // Level filter
  if (selectedLevel.value) {
    filtered = filtered.filter(student => 
      student.vocabulary_level === selectedLevel.value
    )
  }

  return filtered
})

// Toggle student expansion
const toggleStudent = (studentId: string) => {
  if (expandedStudents.value.has(studentId)) {
    expandedStudents.value.delete(studentId)
  } else {
    expandedStudents.value.add(studentId)
  }
}

// Export functions
const exportToCSV = async () => {
  exporting.value = true
  try {
    const csvRows: string[] = []
    
    // Header
    csvRows.push('Student Name,Vocabulary Level,Recommended Words,Last Profile Date')
    
    // Data rows
    filteredStudents.value.forEach(student => {
      const words = student.recommended_words?.map(word => 
        typeof word === 'string' ? word : word.word
      ).join('; ') || 'None'
      csvRows.push([
        student.name,
        student.vocabulary_level || 'N/A',
        words,
        student.last_profile_date ? formatDate(student.last_profile_date) : 'N/A'
      ].join(','))
    })
    
    // Download
    const csvContent = csvRows.join('\n')
    const blob = new Blob([csvContent], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `vocabulary-recommendations-${new Date().toISOString().split('T')[0]}.csv`
    a.click()
    URL.revokeObjectURL(url)
  } catch (error) {
    console.error('Export failed:', error)
  } finally {
    exporting.value = false
  }
}

const exportToPDF = async () => {
  exporting.value = true
  try {
    // TODO: Implement PDF export using a library like jsPDF or pdfmake
    // For now, show a message
    alert('PDF export will be implemented with a PDF library. For now, please use CSV export.')
  } catch (error) {
    console.error('PDF export failed:', error)
  } finally {
    exporting.value = false
  }
}

// View profile details
const viewProfile = (profileId: string) => {
  // TODO: Navigate to profile detail page or show modal
  console.log('View profile:', profileId)
}

// Utility functions
const formatDate = (dateString: string) => {
  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  }).format(new Date(dateString))
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

const getRelicTypeColor = (type: string) => {
  const colors: Record<string, string> = {
    whisper: 'gray',
    echo: 'blue',
    resonance: 'purple',
    thunder: 'red'
  }
  return colors[type] || 'gray'
}

// Fetch on mount
onMounted(() => {
  fetchClasses()
  fetchStudents()
})

useHead({
  title: 'Educator Dashboard - Palabam'
})
</script>

