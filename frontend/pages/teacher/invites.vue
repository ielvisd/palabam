<template>
  <UContainer class="py-8">
    <div class="mb-6">
      <h1 class="text-4xl font-bold mb-2">Manage Invites</h1>
      <p class="text-gray-600 dark:text-gray-400">Send invites to students or generate shareable links</p>
    </div>

    <UTabs :items="tabs" v-model="selectedTab">
      <template #default="{ item }">
        <div class="flex items-center gap-2">
          <UIcon :name="item.icon" class="w-5 h-5" />
          <span>{{ item.label }}</span>
        </div>
      </template>

      <template #send-email>
        <UCard class="mt-4">
          <template #header>
            <h2 class="text-xl font-semibold">Send Email Invites</h2>
          </template>

          <UForm :state="emailForm" class="space-y-4" @submit="handleSendEmail">
            <UFormField label="Class" name="classId" required>
              <USelect
                v-model="emailForm.classId"
                :options="classes.map(c => ({ label: c.name, value: c.id }))"
                placeholder="Select a class"
                :disabled="loadingClasses"
              />
            </UFormField>

            <UFormField label="Student Email(s)" name="emails" required>
              <UTextarea
                v-model="emailForm.emails"
                placeholder="Enter email addresses, one per line"
                :rows="5"
                :disabled="loading"
              />
              <template #help>
                <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
                  Enter one email address per line
                </p>
              </template>
            </UFormField>

            <UButton
              type="submit"
              :loading="loading"
              :disabled="!emailForm.classId || !emailForm.emails"
            >
              Send Invites
            </UButton>
          </UForm>
        </UCard>
      </template>

      <template #generate-link>
        <UCard class="mt-4">
          <template #header>
            <h2 class="text-xl font-semibold">Generate Shareable Link</h2>
          </template>

          <UForm :state="linkForm" class="space-y-4" @submit="handleGenerateLink">
            <UFormField label="Class" name="classId" required>
              <USelect
                v-model="linkForm.classId"
                :options="classes.map(c => ({ label: c.name, value: c.id }))"
                placeholder="Select a class"
                :disabled="loadingClasses"
              />
            </UFormField>

            <UButton
              type="submit"
              :loading="loading"
              :disabled="!linkForm.classId"
            >
              Generate Link
            </UButton>
          </UForm>

          <div v-if="generatedLink" class="mt-4 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
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
        </UCard>
      </template>

      <template #invites-list>
        <div class="mt-4 space-y-4">
          <UCard v-for="invite in invites" :key="invite.id" class="p-4">
            <div class="flex items-center justify-between">
              <div>
                <p class="font-semibold">{{ invite.classes?.name || 'Unknown Class' }}</p>
                <p class="text-sm text-gray-600 dark:text-gray-400">
                  Code: {{ invite.code }}
                  <span v-if="invite.email"> | Email: {{ invite.email }}</span>
                </p>
                <p class="text-xs text-gray-500 dark:text-gray-400">
                  Created: {{ formatDate(invite.created_at) }}
                </p>
              </div>
              <UBadge
                :color="invite.status === 'accepted' ? 'success' : invite.status === 'pending' ? 'warning' : 'error'"
              >
                {{ invite.status }}
              </UBadge>
            </div>
          </UCard>

          <div v-if="invites.length === 0" class="text-center py-8 text-gray-500">
            No invites yet. Create one using the tabs above.
          </div>
        </div>
      </template>
    </UTabs>
  </UContainer>
</template>

<script setup lang="ts">
definePageMeta({
  middleware: 'auth'
})

const config = useRuntimeConfig()
const apiUrl = config.public.apiUrl || 'http://localhost:8000'
const { getTeacherId, sendStudentInviteEmail, generateInviteLink } = useAuth()

const tabs = [
  { label: 'Send Email', value: 'send-email', icon: 'i-heroicons-envelope' },
  { label: 'Generate Link', value: 'generate-link', icon: 'i-heroicons-link' },
  { label: 'All Invites', value: 'invites-list', icon: 'i-heroicons-list-bullet' }
]

const selectedTab = ref('send-email')
const loading = ref(false)
const loadingClasses = ref(false)
const classes = ref<any[]>([])
const invites = ref<any[]>([])
const generatedLink = ref<string | null>(null)

const emailForm = reactive({
  classId: '',
  emails: ''
})

const linkForm = reactive({
  classId: ''
})

// Fetch classes
onMounted(async () => {
  await fetchClasses()
  await fetchInvites()
})

const fetchClasses = async () => {
  loadingClasses.value = true
  try {
    const teacherId = await getTeacherId()
    if (!teacherId) {
      throw new Error('Teacher not found')
    }

    const response = await $fetch(`${apiUrl}/api/classes/teacher/${teacherId}`)
    classes.value = response.classes || []
  } catch (error: any) {
    console.error('Error fetching classes:', error)
  } finally {
    loadingClasses.value = false
  }
}

const fetchInvites = async () => {
  try {
    const teacherId = await getTeacherId()
    if (!teacherId) {
      return
    }

    const response = await $fetch(`${apiUrl}/api/invites?teacher_id=${teacherId}`)
    invites.value = response.invites || []
  } catch (error: any) {
    console.error('Error fetching invites:', error)
  }
}

const handleSendEmail = async () => {
  if (!emailForm.classId || !emailForm.emails) {
    return
  }

  loading.value = true
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
          class_id: emailForm.classId,
          email,
          teacher_id: teacherId
        }
      })
    }

    // Clear form
    emailForm.emails = ''
    
    // Refresh invites list
    await fetchInvites()
    
    alert(`Invites sent to ${emailList.length} student(s)`)
  } catch (error: any) {
    console.error('Error sending invites:', error)
    alert('Failed to send invites: ' + (error.message || 'Unknown error'))
  } finally {
    loading.value = false
  }
}

const handleGenerateLink = async () => {
  if (!linkForm.classId) {
    return
  }

  loading.value = true
  try {
    const teacherId = await getTeacherId()
    if (!teacherId) {
      throw new Error('Teacher not found')
    }

    const response = await $fetch(`${apiUrl}/api/invites/generate`, {
      method: 'POST',
      body: {
        class_id: linkForm.classId,
        teacher_id: teacherId
      }
    })
    generatedLink.value = response.link
    
    // Refresh invites list
    await fetchInvites()
  } catch (error: any) {
    console.error('Error generating link:', error)
    alert('Failed to generate link: ' + (error.message || 'Unknown error'))
  } finally {
    loading.value = false
  }
}

const copyLink = async () => {
  if (generatedLink.value) {
    await navigator.clipboard.writeText(generatedLink.value)
    alert('Link copied to clipboard!')
  }
}

const formatDate = (dateString: string) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString() + ' ' + date.toLocaleTimeString()
}

useHead({
  title: 'Manage Invites - Palabam'
})
</script>

