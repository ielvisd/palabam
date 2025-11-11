<template>
  <UContainer class="py-8">
    <UCard>
      <template #header>
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-3xl font-bold dark:text-white">Parent Dashboard</h1>
            <p class="text-gray-600 dark:text-gray-300 mt-2">View your children's progress</p>
          </div>
          <UButton
            @click="showLinkStudentModal = true"
            color="primary"
            size="lg"
            icon="i-heroicons-user-plus"
          >
            Link Student
          </UButton>
        </div>
      </template>

      <!-- Loading State -->
      <div v-if="loading" class="text-center py-12">
        <UIcon name="i-heroicons-arrow-path" class="animate-spin text-4xl mb-4" />
        <p class="text-gray-600 dark:text-gray-400">Loading children...</p>
      </div>

      <!-- Error State -->
      <UAlert
        v-else-if="error"
        color="error"
        variant="soft"
        :title="error"
        class="mb-6"
      >
        <template #actions>
          <UButton
            color="neutral"
            variant="ghost"
            size="xs"
            @click="fetchChildren"
            class="mt-2"
          >
            Retry
          </UButton>
        </template>
      </UAlert>

      <!-- No Children -->
      <div v-else-if="children.length === 0" class="text-center py-12">
        <UIcon name="i-heroicons-user-group" class="text-6xl text-gray-400 mb-4" />
        <h2 class="text-2xl font-semibold mb-2 dark:text-white">No Children Linked</h2>
        <p class="text-gray-600 dark:text-gray-400 mb-6">
          Link your children's accounts to view their progress
        </p>
        <UButton
          @click="showLinkStudentModal = true"
          color="primary"
          size="lg"
        >
          Link Your First Child
        </UButton>
      </div>

      <!-- Children List -->
      <div v-else class="space-y-6">
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <UCard
            v-for="child in children"
            :key="child.id"
            class="hover:shadow-lg transition-shadow cursor-pointer"
            @click="viewChild(child.id)"
          >
            <div class="space-y-4">
              <div class="flex items-center justify-between">
                <div>
                  <h3 class="text-xl font-semibold dark:text-white">{{ child.name }}</h3>
                  <p class="text-sm text-gray-600 dark:text-gray-400">{{ child.email || 'No email' }}</p>
                </div>
                <UIcon name="i-heroicons-chevron-right" class="text-gray-400" />
              </div>

              <!-- Progress Summary -->
              <div v-if="child.progress" class="space-y-2">
                <div class="flex items-center justify-between">
                  <span class="text-sm text-gray-600 dark:text-gray-400">Level</span>
                  <UBadge
                    :color="getLevelColor(child.progress.vocabulary_level)"
                    size="sm"
                  >
                    {{ child.progress.vocabulary_level || 'Beginner' }}
                  </UBadge>
                </div>
                <div class="flex items-center justify-between">
                  <span class="text-sm text-gray-600 dark:text-gray-400">Streak</span>
                  <span class="font-semibold">{{ child.progress.current_streak || 0 }} days</span>
                </div>
                <div class="flex items-center justify-between">
                  <span class="text-sm text-gray-600 dark:text-gray-400">Stories</span>
                  <span class="font-semibold">{{ child.progress.submission_count || 0 }}</span>
                </div>
                <div class="flex items-center justify-between">
                  <span class="text-sm text-gray-600 dark:text-gray-400">Points</span>
                  <span class="font-semibold">{{ child.progress.total_points || 0 }}</span>
                </div>
              </div>
              <div v-else class="text-center py-4 text-gray-500 text-sm">
                No progress data yet
              </div>

              <UButton
                block
                variant="outline"
                @click.stop="viewChild(child.id)"
              >
                View Details
              </UButton>
            </div>
          </UCard>
        </div>

        <!-- Recent Activity Feed -->
        <div v-if="recentActivity.length > 0" class="mt-8">
          <h2 class="text-xl font-semibold mb-4 dark:text-white">Recent Activity</h2>
          <div class="space-y-2">
            <UCard
              v-for="activity in recentActivity"
              :key="activity.id"
              class="p-4"
            >
              <div class="flex items-center gap-4">
                <div class="flex-1">
                  <div class="font-semibold dark:text-white">{{ activity.studentName }}</div>
                  <div class="text-sm text-gray-600 dark:text-gray-400">
                    {{ activity.description }}
                  </div>
                  <div class="text-xs text-gray-500 dark:text-gray-500 mt-1">
                    {{ formatDate(activity.created_at) }}
                  </div>
                </div>
                <UButton
                  variant="ghost"
                  size="sm"
                  @click="viewChild(activity.studentId)"
                >
                  View
                </UButton>
              </div>
            </UCard>
          </div>
        </div>
      </div>
    </UCard>

    <!-- Link Student Modal -->
    <UModal v-model="showLinkStudentModal">
      <UCard>
        <template #header>
          <h3 class="text-xl font-semibold dark:text-white">Link Student Account</h3>
        </template>

        <UForm :state="linkForm" class="space-y-4" @submit="handleLinkStudent">
          <UFormField label="Student Email" name="email" required>
            <UInput
              v-model="linkForm.email"
              type="email"
              placeholder="Enter student's email address"
              icon="i-heroicons-envelope"
              :disabled="linking"
            />
            <template #help>
              <p class="text-xs text-gray-500 dark:text-gray-400">
                Enter the email address used for the student's account
              </p>
            </template>
          </UFormField>

          <UAlert
            v-if="linkError"
            color="error"
            variant="soft"
            :title="linkError"
            class="mb-4"
            @close="linkError = null"
          />

          <div class="flex gap-2 justify-end">
            <UButton
              variant="ghost"
              @click="showLinkStudentModal = false"
              :disabled="linking"
            >
              Cancel
            </UButton>
            <UButton
              type="submit"
              :loading="linking"
              :disabled="!linkForm.email"
            >
              Link Student
            </UButton>
          </div>
        </UForm>
      </UCard>
    </UModal>
  </UContainer>
</template>

<script setup lang="ts">
definePageMeta({
  middleware: 'parent'
})

const { getParentChildren, linkStudentToParent } = useAuth()
const router = useRouter()
const supabase = useSupabaseClient()
const config = useRuntimeConfig()
const apiUrl = config.public.apiUrl || 'http://localhost:8000'

const loading = ref(true)
const error = ref<string | null>(null)
const children = ref<Array<{
  id: string
  name: string
  email?: string
  student_id: string
  progress?: any
}>>([])
const recentActivity = ref<Array<{
  id: string
  studentId: string
  studentName: string
  description: string
  created_at: string
}>>([])

const showLinkStudentModal = ref(false)
const linking = ref(false)
const linkError = ref<string | null>(null)
const linkForm = reactive({
  email: ''
})

const fetchChildren = async () => {
  loading.value = true
  error.value = null

  try {
    const childrenData = await getParentChildren()
    
    // Fetch progress for each child
    const childrenWithProgress = await Promise.all(
      childrenData.map(async (child) => {
        try {
          // Get student email from users table
          const { data: studentUser } = await supabase
            .from('users')
            .select('email')
            .eq('id', child.student_id)
            .single()

          // Fetch progress
          const progressRes = await $fetch(`${apiUrl}/api/students/${child.id}/progress`)
          
          // Fetch recent submissions for activity feed
          const submissionsRes = await $fetch(`${apiUrl}/api/students/${child.id}/submissions`)
          const recentSubmissions = (submissionsRes.submissions || []).slice(0, 3).map((sub: any) => ({
            id: sub.id,
            studentId: child.id,
            studentName: child.name,
            description: `Submitted ${sub.word_count} word story`,
            created_at: sub.created_at
          }))

          recentActivity.value.push(...recentSubmissions)

          return {
            ...child,
            email: studentUser?.email,
            progress: progressRes
          }
        } catch (err) {
          console.error(`Error fetching progress for ${child.id}:`, err)
          return {
            ...child,
            progress: null
          }
        }
      })
    )

    children.value = childrenWithProgress
    // Sort activity by date
    recentActivity.value.sort((a, b) => 
      new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
    )
    recentActivity.value = recentActivity.value.slice(0, 10) // Keep only 10 most recent
  } catch (err: any) {
    console.error('Failed to fetch children:', err)
    error.value = err.message || 'Failed to load children. Please try again.'
  } finally {
    loading.value = false
  }
}

const handleLinkStudent = async () => {
  if (!linkForm.email) {
    linkError.value = 'Please enter a student email'
    return
  }

  linking.value = true
  linkError.value = null

  try {
    await linkStudentToParent(linkForm.email)
    showLinkStudentModal.value = false
    linkForm.email = ''
    await fetchChildren() // Refresh the list
  } catch (err: any) {
    linkError.value = err.message || 'Failed to link student. Please check the email address.'
  } finally {
    linking.value = false
  }
}

const viewChild = (childId: string) => {
  router.push(`/parent/children/${childId}`)
}

const getLevelColor = (level?: string) => {
  const colors: Record<string, string> = {
    beginner: 'primary',
    intermediate: 'teal',
    advanced: 'yellow',
    expert: 'pink'
  }
  return colors[level || 'beginner'] || 'gray'
}

const formatDate = (dateString: string) => {
  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: 'numeric',
    minute: 'numeric'
  }).format(new Date(dateString))
}

onMounted(() => {
  fetchChildren()
})

useHead({
  title: 'Parent Dashboard - Palabam'
})
</script>

