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

      <div class="space-y-6">
        <!-- Input Section -->
        <div>
          <label class="block text-sm font-medium mb-2">
            {{ isVoiceMode ? 'Voice Input' : 'Text Input' }}
          </label>
          
          <!-- Voice Mode -->
          <div v-if="isVoiceMode" class="space-y-4">
            <div class="flex items-center gap-4">
              <UButton
                :color="isRecording ? 'red' : 'primary'"
                :disabled="isProcessing"
                @click="handleVoiceInput"
                size="xl"
                class="flex-1"
              >
                <template v-if="isRecording">
                  <UIcon name="i-heroicons-stop-circle" class="mr-2" />
                  Stop Recording
                </template>
                <template v-else>
                  <UIcon name="i-heroicons-microphone" class="mr-2" />
                  Start Recording
                </template>
              </UButton>
            </div>
            
            <div v-if="isRecording" class="text-center">
              <div class="inline-flex items-center gap-2 text-red-600">
                <span class="animate-pulse">●</span>
                <span>Recording...</span>
              </div>
            </div>
          </div>

          <!-- Text Mode -->
          <div v-else>
            <UTextarea
              v-model="textInput"
              placeholder="Type your story here..."
              :rows="8"
              size="xl"
              :disabled="isProcessing"
            />
          </div>

          <!-- Transcript Display -->
          <div v-if="transcript" class="mt-4 p-4 bg-gray-50 rounded-lg">
            <p class="text-sm text-gray-600 mb-1">Your input:</p>
            <p class="text-base">{{ transcript }}</p>
          </div>

          <!-- Error Display -->
          <UAlert
            v-if="error"
            color="red"
            variant="soft"
            :title="error"
            class="mt-4"
            @close="error = null"
          />
        </div>

        <!-- Submit Button -->
        <UButton
          :disabled="!canSubmit || isProcessing"
          :loading="isProcessing"
          size="xl"
          color="primary"
          block
          @click="submitStory"
        >
          {{ isProcessing ? 'Analyzing...' : 'Create My Profile' }}
        </UButton>

        <!-- Processing Status -->
        <div v-if="isProcessing" class="text-center">
          <UProgress :value="processingProgress" class="mb-2" />
          <p class="text-sm text-gray-600">{{ processingStatus }}</p>
        </div>

        <!-- Results -->
        <div v-if="profileResult" class="mt-6">
          <UCard>
            <template #header>
              <h2 class="text-2xl font-bold">Your Relic Resonance Profile</h2>
            </template>
            <div class="space-y-4">
              <div>
                <h3 class="font-semibold mb-2">Recommended Words:</h3>
                <div class="flex flex-wrap gap-2">
                  <UBadge
                    v-for="word in profileResult.recommendedWords"
                    :key="word"
                    color="primary"
                    variant="soft"
                    size="lg"
                  >
                    {{ word }}
                  </UBadge>
                </div>
              </div>
              <UButton
                to="/dashboard"
                color="primary"
                size="xl"
                block
              >
                View Dashboard
              </UButton>
            </div>
          </UCard>
        </div>
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
  title: 'Story Spark - Palabam'
})

// Redirect immediately
onMounted(() => {
  navigateTo('/story-spark')
})
</script>

