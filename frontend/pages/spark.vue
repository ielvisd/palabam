<template>
  <UContainer class="py-8">
    <UCard>
      <template #header>
        <div class="flex items-center justify-between">
          <h1 class="text-3xl font-bold">Redirecting...</h1>
        </div>
        <p class="text-gray-600 mt-2">
          Taking you to Story Spark...
        </p>
      </template>

      <div class="text-center py-8">
        <UIcon name="i-heroicons-arrow-path" class="text-4xl text-gray-400 animate-spin mx-auto mb-4" />
        <p class="text-gray-600">Please wait while we redirect you...</p>
      </div>
    </UCard>
  </UContainer>
</template>

<script setup lang="ts">
definePageMeta({
  middleware: 'auth'
})

// Redirect to the main Story Spark page
useHead({
  title: 'Story Spark'
})

// Redirect based on user role
onMounted(async () => {
  const { getUserRole } = useAuth()
  const role = await getUserRole()
  
  // Both students and teachers can access Story Spark
  if (role === 'student' || role === 'teacher') {
    navigateTo('/story-spark')
  } else {
    // For other roles, redirect to their dashboard
    switch (role) {
      case 'parent':
        navigateTo('/parent/dashboard')
        break
      default:
        navigateTo('/')
    }
  }
})
</script>

