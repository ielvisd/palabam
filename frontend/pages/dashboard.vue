<template>
  <UContainer class="py-8">
    <!-- Header Section with Stats -->
    <div class="mb-8">
      <div class="flex items-center justify-between mb-6">
        <div>
          <h1 class="text-4xl font-bold text-navy dark:text-white mb-2">Educator Dashboard</h1>
          <p class="text-gray-600 dark:text-gray-300 text-lg">Vocabulary recommendations for your students</p>
        </div>
        <div class="flex gap-3">
          <UButton
            to="/upload"
            color="primary"
            size="lg"
            icon="i-heroicons-arrow-up-tray"
          >
            Upload Work
          </UButton>
          <UButton
            @click="showCreateClassModal = true"
            variant="outline"
            color="neutral"
            size="lg"
            icon="i-heroicons-plus-circle"
          >
            Create Class
          </UButton>
        </div>
      </div>

      <!-- Quick Stats -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <UCard class="bg-primary/5 border-primary/20">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm text-gray-600 dark:text-gray-300 mb-1">Total Students</p>
              <p class="text-2xl font-bold text-primary">{{ stats.totalStudents }}</p>
            </div>
            <UIcon name="i-heroicons-user-group" class="text-3xl text-primary/40" />
          </div>
        </UCard>
        <UCard class="bg-secondary/5 border-secondary/20">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm text-gray-600 dark:text-gray-300 mb-1">Analyzed</p>
              <p class="text-2xl font-bold text-teal-700 dark:text-teal-400">{{ stats.analyzedStudents }}</p>
            </div>
            <UIcon name="i-heroicons-document-check" class="text-3xl text-secondary/40" />
          </div>
        </UCard>
        <UCard class="bg-teal/5 border-teal/20">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm text-gray-600 dark:text-gray-300 mb-1">Words Recommended</p>
              <p class="text-2xl font-bold text-teal-700 dark:text-teal-400">{{ stats.totalRecommendations }}</p>
            </div>
            <UIcon name="i-heroicons-light-bulb" class="text-3xl text-teal/40" />
          </div>
        </UCard>
        <UCard class="bg-yellow/5 border-yellow/20">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm text-gray-600 dark:text-gray-300 mb-1">My Classes</p>
              <p class="text-2xl font-bold text-yellow-700 dark:text-yellow-400">{{ classes.length }}</p>
            </div>
            <UIcon name="i-heroicons-academic-cap" class="text-3xl text-yellow/40" />
          </div>
        </UCard>
      </div>
    </div>

    <!-- Main Content Card -->
    <UCard>
      <template #header>
        <div class="flex items-center justify-between mb-2">
          <h2 class="text-2xl font-bold text-navy dark:text-white">Student Recommendations</h2>
          <div class="flex gap-3">
            <UButton
              @click="exportToCSV"
              variant="outline"
              color="neutral"
              size="sm"
              :loading="exporting"
              icon="i-heroicons-arrow-down-tray"
            >
              CSV
            </UButton>
            <UButton
              @click="exportToPDF"
              variant="outline"
              color="neutral"
              size="sm"
              :loading="exporting"
              icon="i-heroicons-document-arrow-down"
            >
              PDF
            </UButton>
          </div>
        </div>
      </template>

      <!-- Search and Filter Bar -->
      <div class="mb-6 space-y-4">
        <div class="flex flex-col sm:flex-row gap-4">
          <UInput
            v-model="searchQuery"
            placeholder="Search by student name or word..."
            icon="i-heroicons-magnifying-glass"
            class="flex-1"
            size="lg"
          />
          <USelect
            v-model="selectedLevel"
            :options="vocabularyLevels"
            placeholder="All Levels"
            class="w-48"
            size="lg"
          />
          <UButton
            @click="resetFilters"
            variant="ghost"
            color="neutral"
            size="lg"
            icon="i-heroicons-x-mark"
          >
            Clear
          </UButton>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="text-center py-12">
        <UIcon name="i-heroicons-arrow-path" class="animate-spin text-5xl text-primary mb-4" />
        <p class="text-gray-600 text-lg">Loading student data...</p>
      </div>

      <!-- Students List -->
      <div v-else-if="filteredStudents.length > 0" class="space-y-4">
        <UCard
          v-for="student in filteredStudents"
          :key="student.id"
          class="hover:shadow-lg transition-all duration-200"
          :class="{ 'ring-2 ring-primary': expandedStudents.has(student.id) }"
        >
          <template #header>
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-4 flex-1">
                <div class="flex-1">
                  <div class="flex items-center gap-3 mb-2">
                    <h3 class="text-xl font-semibold text-navy dark:text-white">{{ student.name }}</h3>
                    <div class="flex items-center gap-2">
                      <UBadge
                        :color="getLevelColor(student.vocabulary_level)"
                        variant="soft"
                        size="lg"
                      >
                        {{ formatVocabularyLevel(student.vocabulary_level) }}
                      </UBadge>
                      <span v-if="student.vocabulary_level" class="text-xs text-gray-500 dark:text-gray-400">
                        {{ getVocabularyLevelContext(student.vocabulary_level) }}
                      </span>
                    </div>
                  </div>
                  <div class="flex items-center gap-4 text-sm text-gray-600 dark:text-gray-300">
                    <span class="flex items-center gap-1">
                      <UIcon name="i-heroicons-light-bulb" class="text-teal-700" />
                      {{ getRecommendationCount(student) }} words
                    </span>
                    <span class="flex items-center gap-1">
                      <UIcon name="i-heroicons-calendar" />
                      {{ formatDate(student.last_profile_date) }}
                    </span>
                  </div>
                </div>
              </div>
              <div class="flex items-center gap-2">
                <UButton
                  :to="`/students/${student.id}`"
                  variant="ghost"
                  color="neutral"
                  size="sm"
                  icon="i-heroicons-arrow-top-right-on-square"
                >
                  View Details
                </UButton>
                <UButton
                  @click="toggleStudent(student.id)"
                  variant="ghost"
                  color="neutral"
                  size="sm"
                  :icon="expandedStudents.has(student.id) ? 'i-heroicons-chevron-up' : 'i-heroicons-chevron-down'"
                />
              </div>
            </div>
          </template>

          <!-- Expanded Recommendations -->
          <div v-if="expandedStudents.has(student.id)" class="space-y-6 pt-4 border-t">
            <!-- Recommended Words -->
            <div v-if="student.recommended_words && student.recommended_words.length > 0">
              <h4 class="font-semibold text-lg text-navy dark:text-white mb-4 flex items-center gap-2">
                <UIcon name="i-heroicons-sparkles" class="text-teal-700" />
                Recommended Words ({{ student.recommended_words.length }})
              </h4>
              <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <UCard
                  v-for="word in student.recommended_words"
                  :key="typeof word === 'string' ? word : word.word"
                  class="p-4 hover:shadow-md transition-shadow border-l-4"
                  :class="getWordCardBorderClass(word)"
                >
                  <div class="space-y-3">
                    <div class="flex items-start justify-between">
                      <div class="flex-1">
                        <h5 class="font-bold text-lg text-navy dark:text-white mb-1">
                          {{ typeof word === 'string' ? word : word.word }}
                        </h5>
                        <div class="flex items-center gap-2 flex-wrap">
                          <UBadge
                            v-if="typeof word !== 'string' && word.relic_type"
                            :color="getRelicTypeColor(word.relic_type)"
                            variant="soft"
                            size="xs"
                          >
                            {{ word.relic_type }}
                          </UBadge>
                          <UBadge
                            v-if="typeof word !== 'string' && word.grade_level"
                            color="teal"
                            variant="soft"
                            size="xs"
                          >
                            {{ word.grade_level }} Grade
                          </UBadge>
                          <span v-if="typeof word !== 'string' && word.difficulty_score" class="text-xs text-gray-600 dark:text-gray-300">
                            Difficulty: {{ word.difficulty_score }}/100
                          </span>
                        </div>
                      </div>
                    </div>
                    
                    <p v-if="typeof word !== 'string' && word.definition" class="text-sm text-gray-700 dark:text-gray-300 leading-relaxed">
                      {{ word.definition }}
                    </p>
                    
                    <p v-if="typeof word !== 'string' && word.example" class="text-sm text-gray-600 dark:text-gray-400 italic border-l-2 border-primary pl-3 py-1 bg-gray-50 dark:bg-gray-800 rounded">
                      "{{ word.example }}"
                    </p>
                    
                    <div v-if="typeof word !== 'string' && word.rationale" class="text-xs text-gray-600 dark:text-gray-300 bg-teal/10 dark:bg-teal/20 p-2 rounded flex items-start gap-2">
                      <UIcon name="i-heroicons-light-bulb" class="text-teal-700 mt-0.5 flex-shrink-0" />
                      <span>{{ word.rationale }}</span>
                    </div>
                  </div>
                </UCard>
              </div>
            </div>
            
            <div v-else class="text-center py-8 bg-gray-50 dark:bg-gray-800 rounded-lg">
              <UIcon name="i-heroicons-document-text" class="text-4xl text-gray-400 dark:text-gray-500 mb-3" />
              <p class="text-gray-600 dark:text-gray-300 mb-4">No recommendations yet for this student.</p>
              <UButton
                to="/upload"
                variant="outline"
                color="neutral"
                size="sm"
              >
                Upload Student Work
              </UButton>
            </div>

            <!-- Submission History -->
            <div v-if="student.profiles && student.profiles.length > 0" class="mt-6">
              <h4 class="font-semibold text-lg text-navy dark:text-white mb-3">Submission History</h4>
              <div class="space-y-2">
                  <UCard
                  v-for="profile in student.profiles.slice(0, 5)"
                  :key="profile.id"
                  class="p-3 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
                >
                  <div class="flex items-center justify-between">
                    <div>
                      <span class="text-sm font-medium text-gray-900 dark:text-white">
                        {{ formatDate(profile.created_at) }}
                      </span>
                      <p class="text-xs text-gray-600 dark:text-gray-400 mt-1">
                        {{ profile.resonance_data?.unique_words || 0 }} unique words analyzed
                      </p>
                    </div>
                    <UButton
                      :to="`/students/${student.id}`"
                      variant="ghost"
                      color="neutral"
                      size="xs"
                      icon="i-heroicons-arrow-right"
                    >
                      View
                    </UButton>
                  </div>
                </UCard>
              </div>
            </div>
          </div>
        </UCard>
      </div>

      <!-- Empty State -->
      <div v-else class="text-center py-16">
        <UIcon name="i-heroicons-user-group" class="text-6xl text-gray-300 dark:text-gray-600 mb-4" />
        <h3 class="text-2xl font-semibold text-navy dark:text-white mb-2">No students found</h3>
        <p class="text-gray-600 dark:text-gray-300 mb-6 max-w-md mx-auto">
          {{ searchQuery || selectedLevel ? 'Try adjusting your search filters.' : 'Start by uploading student work to generate vocabulary recommendations.' }}
        </p>
        <div class="flex gap-3 justify-center">
          <UButton
            to="/upload"
            color="primary"
            size="lg"
            icon="i-heroicons-arrow-up-tray"
          >
            Upload First Student Work
          </UButton>
          <UButton
            @click="showCreateClassModal = true"
            variant="outline"
            color="neutral"
            size="lg"
            icon="i-heroicons-academic-cap"
          >
            Create a Class
          </UButton>
        </div>
      </div>
    </UCard>

    <!-- Create Class Modal -->
    <UModal v-model:open="showCreateClassModal" title="Create New Class">
      <template #body>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Class Name</label>
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
        </div>
      </template>
      
      <template #footer="{ close }">
        <div class="flex gap-4">
          <UButton
            @click="createClass"
            color="primary"
            :loading="creatingClass"
            :disabled="!newClassName.trim()"
            block
            size="lg"
          >
            Create Class
          </UButton>
          <UButton
            @click="showCreateClassModal = false"
            variant="outline"
            color="neutral"
            block
            size="lg"
          >
            Cancel
          </UButton>
        </div>
      </template>
    </UModal>

    <!-- Class Created Modal -->
    <UModal v-model:open="showClassCreatedModal">
      <template #header>
        <div class="flex items-center gap-2">
          <UIcon name="i-heroicons-check-circle" class="text-teal-700 dark:text-teal-400 text-3xl" />
          <h2 class="text-2xl font-bold text-navy dark:text-white">Class Created!</h2>
        </div>
      </template>
      
      <template #body>
        <div class="space-y-4">
          <div>
            <p class="text-gray-600 dark:text-gray-300 mb-4">
              Share this code with your students so they can join:
            </p>
            <div class="flex items-center gap-2">
              <div class="flex-1 bg-white dark:bg-gray-800 border-2 border-primary-500 rounded-lg px-6 py-4 text-center">
                <code class="text-4xl font-mono font-bold tracking-widest text-navy-900 dark:text-white block">
                  {{ newClassCode }}
                </code>
              </div>
              <UButton
                @click="copyClassCode(newClassCode)"
                color="primary"
                size="lg"
                icon="i-heroicons-clipboard-document"
              />
            </div>
          </div>
          
          <UAlert color="primary" variant="soft">
            <p class="text-sm">
              Students can join by going to <strong>/join-class</strong> and entering this code.
            </p>
          </UAlert>
        </div>
      </template>
      
      <template #footer="{ close }">
        <UButton
          @click="closeClassCreatedModal"
          color="primary"
          block
          size="lg"
        >
          Done
        </UButton>
      </template>
    </UModal>
  </UContainer>
</template>

<script setup lang="ts">
definePageMeta({
  middleware: 'auth'
})

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
    rationale?: string
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

// Stats
const stats = computed(() => {
  const analyzed = students.value.filter(s => s.vocabulary_level && s.vocabulary_level !== 'Not assessed').length
  const totalRecs = students.value.reduce((sum, s) => sum + getRecommendationCount(s), 0)
  return {
    totalStudents: students.value.length,
    analyzedStudents: analyzed,
    totalRecommendations: totalRecs
  }
})

// Get teacher ID
const { getTeacherId } = useAuth()
const teacherId = ref<string | null>(null)

// Vocabulary levels for filtering (grade levels)
const vocabularyLevels = [
  { label: 'All Grades', value: null },
  { label: 'K-1', value: 'K-1' },
  { label: '2-3', value: '2-3' },
  { label: '4-5', value: '4-5' },
  { label: '6-7', value: '6-7' },
  { label: '8-9', value: '8-9' },
  { label: '10-11', value: '10-11' },
  { label: '12+', value: '12+' }
]

// Fetch data on mount
onMounted(async () => {
  const id = await getTeacherId()
  teacherId.value = id || null
  
  if (teacherId.value) {
    // Fetch classes first, then students (students depend on classes)
    await fetchClasses()
    await fetchStudents()
  }
  loading.value = false
})

// Fetch classes
const fetchClasses = async () => {
  try {
    if (!teacherId.value) return
    const response = await $fetch(`${apiUrl}/api/classes/teacher/${teacherId.value}`) as any
    classes.value = response.classes || []
  } catch (err) {
    console.error('Error fetching classes:', err)
    classes.value = []
  }
}

// Fetch students and recommendations
const fetchStudents = async () => {
  loading.value = true
  try {
    if (!teacherId.value) return
    
    // Get all students from teacher's classes
    const studentMap = new Map<string, Student>()
    
    // Fetch students from all classes
    for (const classItem of classes.value) {
      try {
        const classStudentsResponse = await $fetch(`${apiUrl}/api/students/class/${classItem.id}`) as any
        const classStudents = classStudentsResponse.students || []
        
        for (const student of classStudents) {
          if (!studentMap.has(student.id)) {
            studentMap.set(student.id, {
              id: student.id,
              name: student.name,
              vocabulary_level: undefined,
              recommended_words: [],
              last_profile_date: undefined,
              profiles: []
            })
          }
        }
      } catch (err) {
        console.error(`Error fetching students for class ${classItem.id}:`, err)
      }
    }
    
    // Get latest profiles and recommendations for each student
    for (const [studentId, student] of studentMap.entries()) {
      try {
        // Get latest recommendations from database
        const recsResponse = await $fetch(`${apiUrl}/api/recommend/student/${studentId}`) as any
        if (recsResponse.recommended_words && recsResponse.recommended_words.length > 0) {
          student.recommended_words = recsResponse.recommended_words.map((r: any) => ({
            word: r.word,
            definition: r.definition,
            example: r.example,
            difficulty_score: r.difficulty_score,
            lexile_score: r.lexile_score,
            relic_type: r.relic_type
          }))
        }
        
        // Get latest profile to get vocabulary level and date
        const profilesResponse = await $fetch(`${apiUrl}/api/students/${studentId}/recommendations`).catch(() => null) as any
        if (profilesResponse?.vocabulary_level) {
          student.vocabulary_level = profilesResponse.vocabulary_level
        }
        
        // Try to get profile history (if endpoint exists)
        // For now, we'll use the last_profile_date from recommendations if available
      } catch (err) {
        // Student might not have profiles/recommendations yet
        console.debug(`No recommendations/profiles for student ${studentId}`)
      }
    }
    
    students.value = Array.from(studentMap.values())
  } catch (err: any) {
    console.error('Error fetching students:', err)
    students.value = []
  } finally {
    loading.value = false
  }
}

// Filtered students
const filteredStudents = computed(() => {
  let filtered = [...students.value]
  
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(student => {
      const nameMatch = student.name.toLowerCase().includes(query)
      const wordMatch = student.recommended_words?.some(w => {
        const word = typeof w === 'string' ? w : w.word
        return word.toLowerCase().includes(query)
      })
      return nameMatch || wordMatch
    })
  }
  
  if (selectedLevel.value) {
    filtered = filtered.filter(s => s.vocabulary_level === selectedLevel.value)
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

const resetFilters = () => {
  searchQuery.value = ''
  selectedLevel.value = null
}

// Get recommendation count
const getRecommendationCount = (student: Student): number => {
  return student.recommended_words?.length || 0
}

// Get word card border class
const getWordCardBorderClass = (word: any): string => {
  if (typeof word === 'string') return 'border-l-primary'
  const type = word.relic_type || 'echo'
  const colors: Record<string, string> = {
    whisper: 'border-l-gray-400',
    echo: 'border-l-primary',
    resonance: 'border-l-secondary',
    thunder: 'border-l-pink'
  }
  return colors[type] || 'border-l-primary'
}

// Create class
const createClass = async () => {
  const className = newClassName.value.trim()
  if (!className || !teacherId.value) {
    createClassError.value = 'Please enter a class name.'
    return
  }

  creatingClass.value = true
  createClassError.value = null

  try {
    const response = await $fetch(`${apiUrl}/api/classes/`, {
      method: 'POST',
      body: {
        teacher_id: teacherId.value,
        name: className
      }
    }) as any

    newClassCode.value = response.code
    showCreateClassModal.value = false
    showClassCreatedModal.value = true
    await fetchClasses()
    newClassName.value = ''
  } catch (err: any) {
    createClassError.value = err.data?.detail || err.message || 'Failed to create class.'
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
    // Could show toast notification
  } catch (err) {
    console.error('Failed to copy:', err)
  }
}

// Export functions
const exportToCSV = async () => {
  exporting.value = true
  try {
    const csvRows = []
    csvRows.push(['Student Name', 'Vocabulary Level', 'Recommended Words', 'Definitions', 'Examples'].join(','))
    
    for (const student of students.value) {
      const words = student.recommended_words || []
      if (words.length === 0) {
        csvRows.push([student.name, student.vocabulary_level || '', '', '', ''].join(','))
      } else {
        for (const word of words) {
          const wordText = typeof word === 'string' ? word : word.word
          const definition = typeof word === 'string' ? '' : (word.definition || '')
          const example = typeof word === 'string' ? '' : (word.example || '')
          csvRows.push([
            student.name,
            student.vocabulary_level || '',
            wordText,
            `"${definition}"`,
            `"${example}"`
          ].join(','))
        }
      }
    }
    
    const csvContent = csvRows.join('\n')
    const blob = new Blob([csvContent], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `palabam-recommendations-${new Date().toISOString().split('T')[0]}.csv`
    a.click()
    URL.revokeObjectURL(url)
  } catch (error) {
    console.error('CSV export failed:', error)
    alert('Failed to export CSV. Please try again.')
  } finally {
    exporting.value = false
  }
}

const exportToPDF = async () => {
  exporting.value = true
  try {
    // Dynamic import for jsPDF
    const { jsPDF } = await import('jspdf')
    const doc = new jsPDF()
    
    let y = 20
    doc.setFontSize(18)
    doc.text('Palabam Vocabulary Recommendations', 14, y)
    y += 10
    
    doc.setFontSize(12)
    doc.text(`Generated: ${new Date().toLocaleDateString()}`, 14, y)
    y += 15
    
    for (const student of students.value) {
      if (y > 270) {
        doc.addPage()
        y = 20
      }
      
      doc.setFontSize(14)
      doc.setFont('helvetica', 'bold')
      doc.text(student.name, 14, y)
      y += 7
      
      doc.setFontSize(10)
      doc.setFont('helvetica', 'normal')
      doc.text(`Level: ${student.vocabulary_level || 'Not assessed'}`, 14, y)
      y += 7
      
      const words = student.recommended_words || []
      if (words.length > 0) {
        doc.text('Recommended Words:', 14, y)
        y += 6
        
        for (const word of words.slice(0, 5)) {
          if (y > 270) {
            doc.addPage()
            y = 20
          }
          
          const wordText = typeof word === 'string' ? word : word.word
          const definition = typeof word === 'string' ? '' : (word.definition || '')
          
          doc.setFont('helvetica', 'bold')
          doc.text(`• ${wordText}`, 20, y)
          y += 5
          
          if (definition) {
            doc.setFont('helvetica', 'normal')
            const lines = doc.splitTextToSize(definition, 170)
            doc.text(lines, 25, y)
            y += lines.length * 5
          }
          y += 3
        }
      }
      y += 10
    }
    
    const fileName = `palabam-recommendations-${new Date().toISOString().split('T')[0]}.pdf`
    doc.save(fileName)
  } catch (error) {
    console.error('PDF export failed:', error)
    alert('Failed to generate PDF. Please try again or use CSV export.')
  } finally {
    exporting.value = false
  }
}

// Utility functions
const formatDate = (dateString?: string | null) => {
  if (!dateString) return 'Never'
  try {
    return new Intl.DateTimeFormat('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    }).format(new Date(dateString))
  } catch {
    return 'Invalid date'
  }
}

const formatVocabularyLevel = (level?: string) => {
  if (!level) return 'Not assessed'
  // Make it clear it's a grade level
  if (level.includes('-') || level === '12+') {
    return `${level} grade level`
  }
  // Legacy support
  return level.charAt(0).toUpperCase() + level.slice(1)
}

const getVocabularyLevelContext = (level?: string) => {
  if (!level) return ''
  
  // Grade level mapping for context
  const gradeOrder = ['K-1', '2-3', '4-5', '6-7', '8-9', '10-11', '12+']
  const levelIndex = gradeOrder.indexOf(level)
  
  if (levelIndex === -1) return '' // Legacy levels, no context
  
  // Provide context based on typical expectations
  if (levelIndex <= 1) return '(Early elementary)'
  if (levelIndex <= 2) return '(Elementary)'
  if (levelIndex <= 3) return '(Middle school)'
  if (levelIndex <= 4) return '(High school)'
  return '(Advanced)'
}

const getLevelColor = (level?: string) => {
  if (!level) return 'gray'
  // Grade levels: K-1, 2-3, 4-5, 6-7, 8-9, 10-11, 12+
  const colors: Record<string, string> = {
    'K-1': 'primary',
    '2-3': 'primary',
    '4-5': 'teal',
    '6-7': 'teal',
    '8-9': 'yellow',
    '10-11': 'yellow',
    '12+': 'pink',
    // Legacy support for old categories
    beginner: 'primary',
    intermediate: 'teal',
    advanced: 'yellow',
    expert: 'pink'
  }
  return colors[level] || 'gray'
}

const getRelicTypeColor = (type?: string) => {
  if (!type) return 'gray'
  const colors: Record<string, string> = {
    whisper: 'gray',
    echo: 'primary',
    resonance: 'teal',
    thunder: 'pink'
  }
  return colors[type] || 'gray'
}

useHead({
  title: 'Educator Dashboard - Palabam'
})
</script>
