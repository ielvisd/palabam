<template>
  <UContainer class="py-12">
    <div class="max-w-md mx-auto">
      <UCard>
        <template #header>
          <div class="text-center">
            <h1 class="text-3xl font-bold mb-2">Join Your Class</h1>
            <p class="text-gray-600">Enter the class code your teacher gave you</p>
          </div>
        </template>

        <div class="space-y-6">
          <!-- Class Code Input -->
          <div>
            <label class="block text-sm font-medium mb-2">Class Code</label>
            <UInput
              v-model="classCode"
              placeholder="Enter 6-digit code"
              size="xl"
              :maxlength="6"
              class="text-center text-2xl font-mono tracking-widest uppercase"
              @input="classCode = classCode.toUpperCase().replace(/[^A-Z0-9]/g, '')"
            />
        <p class="text-xs text-gray-600 mt-2">
          Ask your teacher for the class code if you don't have it
        </p>
          </div>

          <!-- Student Name Input -->
          <div>
            <label class="block text-sm font-medium mb-2">Your Name</label>
            <UInput
              v-model="studentName"
              placeholder="Enter your name"
              size="xl"
            />
          </div>

          <!-- Error Display -->
          <UAlert
            v-if="error"
            color="red"
            variant="soft"
            :title="error"
            @close="error = null"
          />

          <!-- Join Button -->
          <UButton
            :disabled="!canJoin || isJoining"
            :loading="isJoining"
            size="xl"
            color="primary"
            block
            @click="joinClass"
          >
            Join Class
          </UButton>

          <!-- Success Message -->
          <UCard v-if="joinSuccess" class="bg-green-50 border-green-200">
            <div class="text-center space-y-4">
              <UIcon name="i-heroicons-check-circle" class="text-green-600 text-4xl" />
              <div>
                <h3 class="text-lg font-semibold text-green-900">Successfully Joined!</h3>
                <p class="text-sm text-gray-600 mt-1">
                  You're now part of {{ classData?.name }}
                </p>
              </div>
              <div class="flex gap-4">
                <UButton
                  to="/story-spark"
                  color="primary"
                  size="lg"
                  block
                >
                  Start Telling Stories
                </UButton>
                <UButton
                  to="/student/dashboard"
                  variant="outline"
                  color="neutral"
                  size="lg"
                  block
                >
                  View My Progress
                </UButton>
              </div>
            </div>
          </UCard>
        </div>
      </UCard>

      <!-- Help Text -->
      <div class="mt-6 text-center text-sm text-gray-600">
        <p>Don't have a class code? Ask your teacher to create a class and share the code with you.</p>
      </div>
    </div>
  </UContainer>
</template>

<script setup lang="ts">
definePageMeta({
  middleware: 'student'
})

const config = useRuntimeConfig()
const apiUrl = config.public.apiUrl || 'http://localhost:8000'
const { getStudentId } = useAuth()

// State
const classCode = ref('')
const studentName = ref('')
const isJoining = ref(false)
const error = ref<string | null>(null)
const joinSuccess = ref(false)
const classData = ref<any>(null)

const canJoin = computed(() => {
  return classCode.value.length === 6 && studentName.value.trim().length > 0
})

const joinClass = async () => {
  if (!canJoin.value) return

  // Additional validation
  if (studentName.value.trim().length < 2) {
    error.value = 'Please enter a valid name (at least 2 characters).'
    return
  }

  isJoining.value = true
  error.value = null

  try {
    // Validate class code first
    const validateRes = await $fetch(`${apiUrl}/api/classes/code/${classCode.value}`)
    
    if (!validateRes) {
      error.value = 'Invalid class code. Please check and try again.'
      isJoining.value = false
      return
    }

    classData.value = validateRes

    // Get student ID from auth (authentication required)
    const studentId = await getStudentId()
    
    if (!studentId) {
      error.value = 'You must be signed in to join a class. Please sign in first.'
      isJoining.value = false
      return
    }

    // Join class
    const response = await $fetch(`${apiUrl}/api/classes/join`, {
      method: 'POST',
      body: {
        code: classCode.value,
        student_id: studentId,
        student_name: studentName.value.trim()
      }
    })

    if (response.success) {
      // Store student name in cookie if not already set
      if (!useCookie('student_name').value) {
        useCookie('student_name').value = studentName.value.trim()
      }
      
      joinSuccess.value = true
    } else {
      error.value = response.message || 'Failed to join class'
    }
  } catch (err: any) {
    // Better error handling
    if (err.statusCode === 404 || err.message?.includes('not found')) {
      error.value = 'Class code not found. Please check and try again.'
    } else if (err.statusCode === 400) {
      error.value = err.message || 'Invalid request. Please check your input.'
    } else if (err.statusCode >= 500) {
      error.value = 'Server error. Please try again later.'
    } else {
      error.value = err.message || 'Failed to join class. Please try again.'
    }
    console.error('Join class error:', err)
  } finally {
    isJoining.value = false
  }
}

useHead({
  title: 'Join Class - Palabam'
})
</script>

