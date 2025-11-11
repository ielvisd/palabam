<template>
  <UContainer>
    <div class="min-h-screen flex items-center justify-center py-12">
      <div class="w-full max-w-md">
        <UCard>
          <template #header>
            <div class="text-center">
              <h1 class="text-3xl font-bold mb-2 dark:text-white">Student Sign Up</h1>
              <p class="text-gray-600 dark:text-gray-400">Create your student account</p>
            </div>
          </template>

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

          <UAlert
            color="warning"
            variant="soft"
            title="Invite Required"
            description="Students must sign up via an invite link from their teacher. Please contact your teacher for an invite link."
            class="mb-4"
          />

          <div class="text-center py-8">
            <UIcon name="i-heroicons-envelope" class="w-16 h-16 mx-auto text-gray-400 mb-4" />
            <p class="text-gray-600 dark:text-gray-400 mb-4">
              To create a student account, you need an invite link from your teacher.
            </p>
            <UButton
              to="/login"
              variant="outline"
            >
              Back to Login
            </UButton>
          </div>

          <div class="mt-6 text-center">
            <p class="text-sm text-gray-600 dark:text-gray-400">
              Already have an account?
              <NuxtLink to="/login" class="text-primary hover:underline font-medium">
                Sign in
              </NuxtLink>
            </p>
          </div>
        </UCard>
      </div>
    </div>
  </UContainer>
</template>

<script setup lang="ts">

useHead({
  title: 'Student Sign Up - Palabam'
})
</script>

