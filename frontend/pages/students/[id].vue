<template>
  <UContainer class="py-8">
    <!-- Header -->
    <div class="mb-6">
      <UButton
        to="/dashboard"
        variant="ghost"
        color="neutral"
        icon="i-heroicons-arrow-left"
        class="mb-4"
      >
        Back to Dashboard
      </UButton>
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-4xl font-bold text-navy mb-2">{{ student?.name || 'Student' }}</h1>
          <p class="text-gray-600">Detailed vocabulary analysis and recommendations</p>
        </div>
        <div class="flex gap-2">
          <UButton
            @click="exportStudentCSV"
            variant="outline"
            color="neutral"
            size="sm"
            :loading="exporting"
            icon="i-heroicons-arrow-down-tray"
          >
            Export CSV
          </UButton>
          <UButton
            @click="exportStudentPDF"
            variant="outline"
            color="neutral"
            size="sm"
            :loading="exporting"
            icon="i-heroicons-document-arrow-down"
          >
            Export PDF
          </UButton>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-12">
      <UIcon name="i-heroicons-arrow-path" class="animate-spin text-5xl text-primary mb-4" />
      <p class="text-gray-600 text-lg">Loading student data...</p>
    </div>

    <!-- Student Content -->
    <div v-else-if="student" class="space-y-6">
      <!-- Summary Cards -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <UCard class="bg-primary/5 border-primary/20">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm text-gray-600 mb-1">Vocabulary Level</p>
              <div class="flex flex-col gap-1">
                <UBadge
                  :color="getLevelColor(student.vocabulary_level)"
                  size="lg"
                  variant="soft"
                >
                  {{ formatVocabularyLevel(student.vocabulary_level) }}
                </UBadge>
                <span v-if="student.vocabulary_level" class="text-xs text-gray-500">
                  {{ getVocabularyLevelContext(student.vocabulary_level) }}
                </span>
              </div>
            </div>
            <UIcon name="i-heroicons-academic-cap" class="text-3xl text-primary/40" />
          </div>
        </UCard>
        <UCard class="bg-secondary/5 border-secondary/20">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm text-gray-600 mb-1">Recommended Words</p>
              <p class="text-2xl font-bold text-teal-700">{{ getRecommendationCount(student) }}</p>
            </div>
            <UIcon name="i-heroicons-light-bulb" class="text-3xl text-secondary/40" />
          </div>
        </UCard>
        <UCard class="bg-teal/5 border-teal/20">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm text-gray-600 mb-1">Submissions</p>
              <p class="text-2xl font-bold text-teal-700">{{ student.profiles?.length || 0 }}</p>
            </div>
            <UIcon name="i-heroicons-document-text" class="text-3xl text-teal/40" />
          </div>
        </UCard>
        <UCard class="bg-yellow/5 border-yellow/20">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm text-gray-600 mb-1">Last Analyzed</p>
              <p class="text-sm font-semibold text-yellow-700">{{ formatDate(student.last_profile_date) }}</p>
            </div>
            <UIcon name="i-heroicons-calendar" class="text-3xl text-yellow/40" />
          </div>
        </UCard>
      </div>

      <!-- Recommended Words -->
      <UCard>
        <template #header>
          <div class="flex items-center gap-2">
            <UIcon name="i-heroicons-sparkles" class="text-teal-700 text-xl" />
            <h2 class="text-2xl font-bold text-navy">Recommended Words</h2>
          </div>
        </template>

        <div v-if="student.recommended_words && student.recommended_words.length > 0" class="space-y-4">
          <p class="text-gray-600">
            Personalized vocabulary recommendations based on {{ student.name }}'s writing level and patterns.
          </p>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <UCard
              v-for="word in student.recommended_words"
              :key="typeof word === 'string' ? word : word.word"
              class="p-5 hover:shadow-lg transition-all border-l-4"
              :class="getWordCardBorderClass(word)"
            >
              <div class="space-y-3">
                <div class="flex items-start justify-between">
                  <div class="flex-1">
                    <h3 class="font-bold text-xl text-navy mb-2">
                      {{ typeof word === 'string' ? word : word.word }}
                    </h3>
                    <div class="flex items-center gap-2 flex-wrap mb-2">
                      <UBadge
                        v-if="typeof word !== 'string' && word.relic_type"
                        :color="getRelicTypeColor(word.relic_type)"
                        variant="soft"
                        size="sm"
                      >
                        {{ word.relic_type }}
                      </UBadge>
                      <div class="flex items-center gap-2 flex-wrap">
                        <UBadge
                          v-if="typeof word !== 'string' && word.grade_level"
                          color="teal"
                          variant="soft"
                          size="xs"
                        >
                          {{ word.grade_level }} Grade
                        </UBadge>
                        <span v-if="typeof word !== 'string' && word.difficulty_score" class="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">
                          Difficulty: {{ word.difficulty_score }}/100
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
                
                <p v-if="typeof word !== 'string' && word.definition" class="text-sm text-gray-700 leading-relaxed">
                  {{ word.definition }}
                </p>
                
                <p v-if="typeof word !== 'string' && word.example" class="text-sm text-gray-600 italic border-l-2 border-primary pl-3 py-2 bg-gray-50 rounded">
                  "{{ word.example }}"
                </p>
                
                <div v-if="typeof word !== 'string' && word.rationale" class="text-xs text-gray-600 bg-teal/10 p-3 rounded flex items-start gap-2">
                  <UIcon name="i-heroicons-light-bulb" class="text-teal-700 mt-0.5 flex-shrink-0" />
                  <span>{{ word.rationale }}</span>
                </div>
              </div>
            </UCard>
          </div>
        </div>
        <div v-else class="text-center py-12">
          <UIcon name="i-heroicons-document-text" class="text-4xl text-gray-400 mb-3" />
          <p class="text-gray-600 mb-4">No recommendations yet for this student.</p>
          <UButton
            to="/upload"
            variant="outline"
            color="neutral"
            size="sm"
          >
            Upload Student Work
          </UButton>
        </div>
      </UCard>

      <!-- Submission Timeline -->
      <UCard v-if="student.profiles && student.profiles.length > 0">
        <template #header>
          <div class="flex items-center gap-2">
            <UIcon name="i-heroicons-clock" class="text-primary text-xl" />
            <h2 class="text-2xl font-bold text-navy">Submission History</h2>
          </div>
        </template>

        <ProfileHistory
          :profiles="student.profiles || []"
          :student-id="studentId"
          :loading="loading"
          :show-actions="false"
        />
      </UCard>
    </div>

    <!-- Not Found -->
    <div v-else class="text-center py-16">
      <UIcon name="i-heroicons-user" class="text-6xl text-gray-300 mb-4" />
      <h3 class="text-2xl font-semibold text-navy mb-2">Student Not Found</h3>
      <p class="text-gray-600 mb-6">This student doesn't exist or you don't have access.</p>
      <UButton
        to="/dashboard"
        color="primary"
        size="lg"
      >
        Back to Dashboard
      </UButton>
    </div>
  </UContainer>
</template>

<script setup lang="ts">
definePageMeta({
  middleware: 'auth'
})

const route = useRoute()
const config = useRuntimeConfig()
const apiUrl = config.public.apiUrl || 'http://localhost:8000'

const studentId = route.params.id as string

// State
const loading = ref(true)
const exporting = ref(false)
const student = ref<any>(null)

// Fetch student data
onMounted(async () => {
  loading.value = true
  try {
    // Fetch student details
    const studentData = await $fetch(`${apiUrl}/api/students/${studentId}`).catch(() => null)
    
    // Fetch latest recommendations from database
    const recommendationsResponse = await $fetch(`${apiUrl}/api/recommend/student/${studentId}`).catch(() => ({ recommended_words: [] }))
    const recommendations = recommendationsResponse.recommended_words || []
    
    // Fetch vocabulary level from profile endpoint
    const profileResponse = await $fetch(`${apiUrl}/api/students/${studentId}/recommendations`).catch(() => ({ vocabulary_level: null }))
    
    // Fetch profile history (if endpoint exists, otherwise use db directly)
    // For now, we'll try to get from profiles table via Supabase client
    const supabase = useSupabaseClient()
    const { data: profilesData } = await supabase
      .from('profiles')
      .select('*')
      .eq('student_id', studentId)
      .order('created_at', { ascending: false })
      .limit(20)
    
    student.value = {
      ...studentData,
      vocabulary_level: profileResponse.vocabulary_level || studentData?.vocabulary_level,
      recommended_words: recommendations.map((r: any) => ({
        word: r.word,
        definition: r.definition,
        example: r.example,
        difficulty_score: r.difficulty_score,
        lexile_score: r.lexile_score,
        relic_type: r.relic_type
      })),
      profiles: profilesData || [],
      last_profile_date: profilesData?.[0]?.created_at
    }
  } catch (err) {
    console.error('Error fetching student:', err)
  } finally {
    loading.value = false
  }
})

// Export functions
const exportStudentCSV = async () => {
  if (!student.value) return
  
  exporting.value = true
  try {
    const csvRows = []
    csvRows.push(['Word', 'Definition', 'Example', 'Difficulty', 'Rationale'].join(','))
    
    const words = student.value.recommended_words || []
    for (const word of words) {
      const wordText = typeof word === 'string' ? word : word.word
      const definition = typeof word === 'string' ? '' : (word.definition || '')
      const example = typeof word === 'string' ? '' : (word.example || '')
      const difficulty = typeof word === 'string' ? '' : (word.difficulty_score || '')
      const rationale = typeof word === 'string' ? '' : (word.rationale || '')
      
      csvRows.push([
        wordText,
        `"${definition}"`,
        `"${example}"`,
        difficulty,
        `"${rationale}"`
      ].join(','))
    }
    
    const csvContent = csvRows.join('\n')
    const blob = new Blob([csvContent], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `palabam-${student.value.name}-${new Date().toISOString().split('T')[0]}.csv`
    a.click()
    URL.revokeObjectURL(url)
  } catch (error) {
    console.error('CSV export failed:', error)
    alert('Failed to export CSV. Please try again.')
  } finally {
    exporting.value = false
  }
}

const exportStudentPDF = async () => {
  if (!student.value) return
  
  exporting.value = true
  try {
    const { jsPDF } = await import('jspdf')
    const doc = new jsPDF()
    
    let y = 20
    doc.setFontSize(18)
    doc.text(`Vocabulary Recommendations: ${student.value.name}`, 14, y)
    y += 10
    
    doc.setFontSize(12)
    doc.text(`Generated: ${new Date().toLocaleDateString()}`, 14, y)
    doc.text(`Vocabulary Level: ${student.value.vocabulary_level || 'Not assessed'}`, 14, y + 7)
    y += 15
    
    const words = student.value.recommended_words || []
    if (words.length > 0) {
      doc.setFontSize(14)
      doc.setFont(undefined, 'bold')
      doc.text('Recommended Words:', 14, y)
      y += 8
      
      for (const word of words) {
        if (y > 270) {
          doc.addPage()
          y = 20
        }
        
        const wordText = typeof word === 'string' ? word : word.word
        const definition = typeof word === 'string' ? '' : (word.definition || '')
        const example = typeof word === 'string' ? '' : (word.example || '')
        
        doc.setFontSize(12)
        doc.setFont(undefined, 'bold')
        doc.text(`• ${wordText}`, 20, y)
        y += 6
        
        if (definition) {
          doc.setFont(undefined, 'normal')
          const lines = doc.splitTextToSize(definition, 170)
          doc.text(lines, 25, y)
          y += lines.length * 5
        }
        
        if (example) {
          doc.setFont(undefined, 'italic')
          const exampleLines = doc.splitTextToSize(`"${example}"`, 170)
          doc.text(exampleLines, 25, y)
          y += exampleLines.length * 5
        }
        y += 5
      }
    }
    
    const fileName = `palabam-${student.value.name}-${new Date().toISOString().split('T')[0]}.pdf`
    doc.save(fileName)
  } catch (error) {
    console.error('PDF export failed:', error)
    alert('Failed to generate PDF. Please try again or use CSV export.')
  } finally {
    exporting.value = false
  }
}

// Utility functions
const getRecommendationCount = (student: any): number => {
  return student.recommended_words?.length || 0
}

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

const formatDate = (dateString?: string) => {
  if (!dateString) return 'Never'
  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: 'numeric',
    minute: '2-digit'
  }).format(new Date(dateString))
}

useHead({
  title: `${student.value?.name || 'Student'} - Palabam`
})
</script>

