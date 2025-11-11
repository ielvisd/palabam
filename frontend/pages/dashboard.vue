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

    <!-- Main Content Card with Tabs -->
    <UCard>
      <template #header>
        <div class="flex items-center justify-between mb-2">
          <h2 class="text-2xl font-bold text-navy dark:text-white">Dashboard</h2>
          <div v-if="selectedTab === 'students'" class="flex gap-3">
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

      <UTabs :items="dashboardTabs" v-model="selectedTab">
        <!-- Students Tab -->
        <template #students>
          <div class="mt-6">
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
              <ProfileHistory
                :profiles="student.profiles"
                :student-id="student.id"
                title="Submission History"
                :limit="5"
                :show-actions="true"
                @profile-click="() => navigateTo(`/students/${student.id}`)"
              />
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
          </div>
        </template>

        <!-- Classes Tab -->
        <template #classes>
          <div class="mt-6">
            <!-- Loading State -->
            <div v-if="loadingClasses" class="text-center py-12">
              <UIcon name="i-heroicons-arrow-path" class="animate-spin text-5xl text-primary mb-4" />
              <p class="text-gray-600 text-lg">Loading classes...</p>
            </div>

            <!-- Classes Grid -->
            <div v-else-if="classes.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <UCard
                v-for="classItem in classes"
                :key="classItem.id"
                class="hover:shadow-lg transition-all duration-200 cursor-pointer"
                @click="openClassModal(classItem)"
              >
                <div class="flex justify-between items-start">
                  <div class="flex-1">
                    <h3 class="text-xl font-semibold text-navy dark:text-white mb-2">{{ classItem.name }}</h3>
                    <p class="text-sm text-gray-600 dark:text-gray-400">
                      <span class="font-medium">{{ getClassStudentCount(classItem.id) }}</span> students
                    </p>
                  </div>
                  <UButton
                    variant="ghost"
                    color="neutral"
                    size="sm"
                    icon="i-heroicons-chevron-right"
                    @click.stop="openClassModal(classItem)"
                  />
                </div>
              </UCard>
            </div>

            <!-- Empty State -->
            <div v-else class="text-center py-16">
              <UIcon name="i-heroicons-academic-cap" class="text-6xl text-gray-300 dark:text-gray-600 mb-4" />
              <h3 class="text-2xl font-semibold text-navy dark:text-white mb-2">No classes yet</h3>
              <p class="text-gray-600 dark:text-gray-300 mb-6 max-w-md mx-auto">
                Create your first class to start inviting students.
              </p>
              <UButton
                @click="showCreateClassModal = true"
                color="primary"
                size="lg"
                icon="i-heroicons-plus-circle"
              >
                Create Your First Class
              </UButton>
            </div>
          </div>
        </template>
      </UTabs>
    </UCard>

    <!-- Create Class Modal -->
    <UModal 
      v-model:open="showCreateClassModal" 
      title="Create New Class"
      description="Enter a name for your new class. You'll be able to generate invite links to share with students."
    >
      <template #body>
        <form id="create-class-form" class="space-y-4" @submit.prevent="createClass">
          <UFormField label="Class Name" name="className">
            <UInput
              v-model="newClassName"
              placeholder="e.g., 7th Grade ELA - Period 1"
              size="lg"
              :disabled="creatingClass"
            />
            <template #help>
              <p class="text-sm text-gray-500 dark:text-gray-400">
                Enter a descriptive name for your class. This will help you identify it later.
              </p>
            </template>
          </UFormField>
          
          <UAlert
            v-if="createClassError"
            color="red"
            variant="soft"
            :title="createClassError"
            @close="createClassError = null"
          />
        </form>
      </template>
      
      <template #footer="{ close }">
        <div class="flex gap-4">
          <UButton
            type="submit"
            form="create-class-form"
            color="primary"
            :loading="creatingClass"
            :disabled="!newClassName || !newClassName.trim() || creatingClass"
            block
            size="lg"
          >
            Create Class
          </UButton>
          <UButton
            type="button"
            @click="showCreateClassModal = false"
            variant="outline"
            color="neutral"
            block
            size="lg"
            :disabled="creatingClass"
          >
            Cancel
          </UButton>
        </div>
      </template>
    </UModal>

    <!-- Class Created Modal -->
    <UModal 
      v-model:open="showClassCreatedModal"
      title="Class Created!"
      description="Your class has been created. Generate an invite link to share with your students."
    >
      <template #header>
        <div class="flex items-center gap-2">
          <UIcon name="i-heroicons-check-circle" class="text-teal-700 dark:text-teal-400 text-3xl" />
          <h2 class="text-2xl font-bold text-navy dark:text-white">Class Created!</h2>
        </div>
      </template>
      
      <template #body>
        <div class="space-y-4">
          <p class="text-gray-600 dark:text-gray-300">
            Go to the <strong>Classes</strong> tab, click on this class, and use the <strong>Invite</strong> tab to generate a shareable link for your students.
          </p>
          
          <UAlert color="primary" variant="soft">
            <p class="text-sm">
              Students can join by clicking the invite link you share with them.
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

    <!-- Class Detail Modal -->
    <UModal 
      v-model:open="showClassDetailModal"
      :title="selectedClass ? selectedClass.name : 'Class Details'"
    >
      <template #body>
        <div v-if="selectedClass" class="space-y-6">
          <UTabs :items="classModalTabs" v-model="selectedClassModalTab">
            <!-- Overview Tab -->
            <template #overview>
              <div class="space-y-6 mt-4">
                <!-- Class Info -->
                <div>
                  <h3 class="text-lg font-semibold text-navy dark:text-white mb-4">Class Information</h3>
                  <div class="space-y-3">
                    <div>
                      <p class="text-sm text-gray-600 dark:text-gray-400 mb-1">Students</p>
                      <p class="text-lg font-semibold text-navy dark:text-white">
                        {{ classStudents.length }} enrolled
                      </p>
                    </div>
                  </div>
                </div>

                <!-- Students List -->
                <div>
                  <h3 class="text-lg font-semibold text-navy dark:text-white mb-4">Enrolled Students</h3>
                  <div v-if="loadingClassStudents" class="text-center py-8">
                    <UIcon name="i-heroicons-arrow-path" class="animate-spin text-3xl text-primary mb-2" />
                    <p class="text-sm text-gray-600">Loading students...</p>
                  </div>
                  <div v-else-if="classStudents.length > 0" class="space-y-2">
                    <UCard
                      v-for="student in classStudents"
                      :key="student.id"
                      class="p-3 hover:shadow-md transition"
                    >
                      <div class="flex items-center justify-between">
                        <div class="flex items-center gap-3">
                          <UIcon name="i-heroicons-user" class="text-gray-400" />
                          <span class="font-medium text-navy dark:text-white">{{ student.name }}</span>
                        </div>
                        <UButton
                          :to="`/students/${student.id}`"
                          variant="ghost"
                          color="neutral"
                          size="sm"
                          icon="i-heroicons-arrow-top-right-on-square"
                        >
                          View
                        </UButton>
                      </div>
                    </UCard>
                  </div>
                  <div v-else class="text-center py-8 bg-gray-50 dark:bg-gray-800 rounded-lg">
                    <UIcon name="i-heroicons-user-group" class="text-4xl text-gray-400 mb-3" />
                    <p class="text-gray-600 dark:text-gray-300">No students enrolled yet</p>
                  </div>
                </div>
              </div>
            </template>

            <!-- Invite Tab -->
            <template #invite>
              <div class="mt-4">
                <UTabs :items="inviteTabs" v-model="selectedInviteTab">
                  <!-- Send Email Tab -->
                  <template #send-email>
                    <div class="mt-4">
                      <UForm :state="emailForm" class="space-y-4" @submit="handleSendEmail">
                        <UFormField label="Student Email(s)" name="emails" required>
                          <UTextarea
                            v-model="emailForm.emails"
                            placeholder="Enter email addresses, one per line"
                            :rows="5"
                            :disabled="loadingInvite"
                          />
                          <template #help>
                            <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
                              Enter one email address per line
                            </p>
                          </template>
                        </UFormField>

                        <UButton
                          type="submit"
                          :loading="loadingInvite"
                          :disabled="!emailForm.emails"
                          block
                        >
                          Send Invites
                        </UButton>
                      </UForm>
                    </div>
                  </template>

                  <!-- Generate Link Tab -->
                  <template #generate-link>
                    <div class="mt-4 space-y-4">
                      <UButton
                        @click="handleGenerateLink"
                        :loading="loadingInvite"
                        block
                      >
                        Generate Invite Link
                      </UButton>

                      <div v-if="generatedLink" class="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
                        <p class="text-sm font-semibold mb-2">Invite Link:</p>
                        <div class="flex gap-2">
                          <UInput
                            :model-value="generatedLink"
                            readonly
                            class="flex-1"
                          />
                          <UButton
                            @click="copyLink"
                            icon="i-heroicons-clipboard"
                            variant="outline"
                          >
                            Copy
                          </UButton>
                        </div>
                        <p class="text-xs text-gray-500 dark:text-gray-400 mt-2">
                          Share this link with students. They can use it to sign up and join your class.
                        </p>
                      </div>
                    </div>
                  </template>
                </UTabs>
              </div>
            </template>
          </UTabs>
        </div>
      </template>
      
      <template #footer="{ close }">
        <UButton
          @click="closeClassDetailModal"
          color="primary"
          block
          size="lg"
        >
          Close
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
const creatingClass = ref(false)
const createClassError = ref<string | null>(null)

// Dashboard tabs
const selectedTab = ref('students')
const dashboardTabs = [
  { label: 'Students', value: 'students', slot: 'students', icon: 'i-heroicons-user-group' },
  { label: 'Classes', value: 'classes', slot: 'classes', icon: 'i-heroicons-academic-cap' }
]

// Class detail modal state
const showClassDetailModal = ref(false)
const selectedClass = ref<any>(null)
const classStudents = ref<any[]>([])
const loadingClassStudents = ref(false)
const selectedClassModalTab = ref('overview')
const classModalTabs = [
  { label: 'Overview', value: 'overview', slot: 'overview', icon: 'i-heroicons-information-circle' },
  { label: 'Invite', value: 'invite', slot: 'invite', icon: 'i-heroicons-envelope' }
]

// Invite functionality state
const selectedInviteTab = ref('send-email')
const inviteTabs = [
  { label: 'Send Email', value: 'send-email', slot: 'send-email', icon: 'i-heroicons-envelope' },
  { label: 'Generate Link', value: 'generate-link', slot: 'generate-link', icon: 'i-heroicons-link' }
]
const emailForm = reactive({
  emails: ''
})
const generatedLink = ref<string | null>(null)
const loadingInvite = ref(false)
const loadingClasses = ref(false)

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
    await fetchClassStudentCounts()
    await fetchStudents()
  }
  loading.value = false
})

// Watch for class modal opening to fetch students
watch(showClassDetailModal, async (isOpen) => {
  if (isOpen && selectedClass.value) {
    await fetchClassStudents(selectedClass.value.id)
  }
})

// Watch for modal opening and ensure teacherId is available
watch(showCreateClassModal, async (isOpen) => {
  if (isOpen && !teacherId.value) {
    // Try to fetch teacherId when modal opens
    const id = await getTeacherId()
    if (id) {
      teacherId.value = id
    }
  }
  // Clear any previous errors when opening modal
  if (isOpen) {
    createClassError.value = null
    newClassName.value = ''
  }
})

// Fetch classes
const fetchClasses = async () => {
  loadingClasses.value = true
  try {
    if (!teacherId.value) return
    const response = await $fetch(`${apiUrl}/api/classes/teacher/${teacherId.value}`) as any
    classes.value = response.classes || []
  } catch (err) {
    console.error('Error fetching classes:', err)
    classes.value = []
  } finally {
    loadingClasses.value = false
  }
}

// Map to track student counts per class
const classStudentCounts = ref<Map<string, number>>(new Map())

// Get student count for a class
const getClassStudentCount = (classId: string): number => {
  return classStudentCounts.value.get(classId) || 0
}

// Fetch student counts for all classes
const fetchClassStudentCounts = async () => {
  if (!teacherId.value) return
  
  const counts = new Map<string, number>()
  for (const classItem of classes.value) {
    try {
      const response = await $fetch(`${apiUrl}/api/students/class/${classItem.id}`) as any
      counts.set(classItem.id, (response.students || []).length)
    } catch (err) {
      console.error(`Error fetching student count for class ${classItem.id}:`, err)
      counts.set(classItem.id, 0)
    }
  }
  classStudentCounts.value = counts
}

// Open class detail modal
const openClassModal = async (classItem: any) => {
  selectedClass.value = classItem
  showClassDetailModal.value = true
  selectedClassModalTab.value = 'overview'
  selectedInviteTab.value = 'send-email'
  generatedLink.value = null
  emailForm.emails = ''
  await fetchClassStudents(classItem.id)
}

// Close class detail modal
const closeClassDetailModal = () => {
  showClassDetailModal.value = false
  selectedClass.value = null
  classStudents.value = []
  generatedLink.value = null
  emailForm.emails = ''
}

// Fetch students for a specific class
const fetchClassStudents = async (classId: string) => {
  loadingClassStudents.value = true
  try {
    const response = await $fetch(`${apiUrl}/api/students/class/${classId}`) as any
    classStudents.value = response.students || []
    // Update the count in our map
    classStudentCounts.value.set(classId, classStudents.value.length)
  } catch (err) {
    console.error('Error fetching class students:', err)
    classStudents.value = []
  } finally {
    loadingClassStudents.value = false
  }
}

// Handle sending email invites
const handleSendEmail = async () => {
  if (!emailForm.emails || !selectedClass.value) {
    return
  }

  loadingInvite.value = true
  try {
    const teacherId = await getTeacherId()
    if (!teacherId) {
      throw new Error('Teacher not found')
    }

    const emailList = emailForm.emails
      .split('\n')
      .map(e => e.trim())
      .filter(e => e.length > 0)

    // Send invites for each email
    for (const email of emailList) {
      await $fetch(`${apiUrl}/api/invites/email`, {
        method: 'POST',
        body: {
          class_id: selectedClass.value.id,
          email,
          teacher_id: teacherId
        }
      })
    }

    // Clear form
    emailForm.emails = ''
    
    alert(`Invites sent to ${emailList.length} student(s)`)
  } catch (error: any) {
    console.error('Error sending invites:', error)
    alert('Failed to send invites: ' + (error.message || 'Unknown error'))
  } finally {
    loadingInvite.value = false
  }
}

// Handle generating invite link
const handleGenerateLink = async () => {
  if (!selectedClass.value) {
    return
  }

  loadingInvite.value = true
  try {
    const teacherId = await getTeacherId()
    if (!teacherId) {
      throw new Error('Teacher not found')
    }

    const response = await $fetch(`${apiUrl}/api/invites/generate`, {
      method: 'POST',
      body: {
        class_id: selectedClass.value.id,
        teacher_id: teacherId
      }
    }) as any
    generatedLink.value = response.link
  } catch (error: any) {
    console.error('Error generating link:', error)
    alert('Failed to generate link: ' + (error.message || 'Unknown error'))
  } finally {
    loadingInvite.value = false
  }
}

// Copy invite link
const copyLink = async () => {
  if (generatedLink.value) {
    await navigator.clipboard.writeText(generatedLink.value)
    alert('Link copied to clipboard!')
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
  if (!className) {
    createClassError.value = 'Please enter a class name.'
    return
  }
  
  // Ensure teacherId is available
  if (!teacherId.value) {
    // Try to fetch it if not available
    const id = await getTeacherId()
    if (id) {
      teacherId.value = id
    } else {
      console.error('Teacher ID not found. User may not have a teacher record.')
      createClassError.value = 'Unable to create class. You must be logged in as a teacher. Please refresh the page and try again.'
      return
    }
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

    showCreateClassModal.value = false
    showClassCreatedModal.value = true
    await fetchClasses()
    await fetchClassStudentCounts()
    newClassName.value = ''
  } catch (err: any) {
    createClassError.value = err.data?.detail || err.message || 'Failed to create class.'
  } finally {
    creatingClass.value = false
  }
}

const closeClassCreatedModal = () => {
  showClassCreatedModal.value = false
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
