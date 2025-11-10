<template>
  <UContainer class="py-8">
    <UCard>
      <template #header>
        <h1 class="text-3xl font-bold">Legend Ledger</h1>
        <p class="text-gray-600 mt-2">Your vocabulary mastery journey</p>
      </template>

      <div class="space-y-8">
        <!-- Stats Overview -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
          <UCard>
            <div class="text-center">
              <div class="text-3xl font-bold text-primary">{{ streak }}</div>
              <div class="text-sm text-gray-600 mt-1">Day Streak</div>
            </div>
          </UCard>
          <UCard>
            <div class="text-center">
              <div class="text-3xl font-bold text-green-600">{{ masteredWords }}</div>
              <div class="text-sm text-gray-600 mt-1">Words Mastered</div>
            </div>
          </UCard>
          <UCard>
            <div class="text-center">
              <div class="text-3xl font-bold text-blue-600">{{ totalSessions }}</div>
              <div class="text-sm text-gray-600 mt-1">Sessions Completed</div>
            </div>
          </UCard>
          <UCard>
            <div class="text-center">
              <div class="text-3xl font-bold text-purple-600">{{ Math.round(overallMastery) }}%</div>
              <div class="text-sm text-gray-600 mt-1">Overall Mastery</div>
            </div>
          </UCard>
        </div>

        <!-- Progress Timeline -->
        <div>
          <h2 class="text-xl font-semibold mb-4">Progress Timeline</h2>
          <UTimeline>
            <UTimelineItem
              v-for="(milestone, index) in milestones"
              :key="index"
              :title="milestone.title"
              :description="milestone.description"
              :time="milestone.date"
              :icon="milestone.icon"
            />
          </UTimeline>
        </div>

        <!-- Word Mastery Progress -->
        <div>
          <h2 class="text-xl font-semibold mb-4">Word Mastery</h2>
          <div class="space-y-3">
            <div
              v-for="word in wordProgress"
              :key="word.id"
              class="p-4 bg-gray-50 rounded-lg"
            >
              <div class="flex items-center justify-between mb-2">
                <div class="flex items-center gap-3">
                  <span class="text-lg font-semibold">{{ word.word }}</span>
                  <UBadge :color="getRelicTypeColor(word.relicType)" variant="soft">
                    {{ word.relicType }}
                  </UBadge>
                </div>
                <div class="text-sm text-gray-600">
                  {{ Math.round(word.mastery * 100) }}% Mastered
                </div>
              </div>
              <UProgress
                :value="word.mastery * 100"
                :max="100"
                :color="getMasteryColor(word.mastery)"
              />
              <div class="mt-2 text-sm text-gray-600">
                <span>Repetitions: {{ word.repetitions }}</span>
                <span class="ml-4">Next Review: {{ formatDate(word.dueDate) }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Relic Collection -->
        <div>
          <h2 class="text-xl font-semibold mb-4">Relic Collection</h2>
          <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
            <UCard
              v-for="(count, type) in relicDistribution"
              :key="type"
              class="text-center"
            >
              <div class="text-2xl font-bold" :class="getRelicTypeTextColor(type)">
                {{ count }}
              </div>
              <div class="text-sm text-gray-600 mt-1 capitalize">{{ type }} Relics</div>
            </UCard>
          </div>
        </div>

        <!-- Recent Sessions -->
        <div>
          <h2 class="text-xl font-semibold mb-4">Recent Sessions</h2>
          <div class="space-y-2">
            <UCard
              v-for="session in recentSessions"
              :key="session.id"
              class="p-4"
            >
              <div class="flex items-center justify-between">
                <div>
                  <div class="font-semibold">{{ formatDate(session.date) }}</div>
                  <div class="text-sm text-gray-600">
                    {{ session.wordsPracticed }} words practiced
                  </div>
                </div>
                <UBadge :color="session.completed ? 'green' : 'gray'">
                  {{ session.completed ? 'Completed' : 'In Progress' }}
                </UBadge>
              </div>
            </UCard>
          </div>
        </div>
      </div>
    </UCard>
  </UContainer>
</template>

<script setup lang="ts">
import { useSRS } from '@/composables/useSRS'

const { getProgressStats } = useSRS()

// Mock data - in production, fetch from Supabase
const streak = ref(7)
const masteredWords = ref(42)
const totalSessions = ref(15)
const overallMastery = ref(68)

const milestones = ref([
  {
    title: 'First Session Completed',
    description: 'Started your vocabulary journey',
    date: '2 weeks ago',
    icon: 'i-heroicons-star'
  },
  {
    title: '10 Words Mastered',
    description: 'Reached your first milestone',
    date: '1 week ago',
    icon: 'i-heroicons-trophy'
  },
  {
    title: '7 Day Streak',
    description: 'Consistent practice!',
    date: 'Today',
    icon: 'i-heroicons-fire'
  }
])

const wordProgress = ref([
  {
    id: '1',
    word: 'resilient',
    relicType: 'resonance',
    mastery: 0.85,
    repetitions: 5,
    dueDate: new Date(Date.now() + 3 * 24 * 60 * 60 * 1000)
  },
  {
    id: '2',
    word: 'perseverance',
    relicType: 'thunder',
    mastery: 0.45,
    repetitions: 2,
    dueDate: new Date(Date.now() + 1 * 24 * 60 * 60 * 1000)
  },
  {
    id: '3',
    word: 'curious',
    relicType: 'echo',
    mastery: 0.95,
    repetitions: 8,
    dueDate: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000)
  }
])

const relicDistribution = computed(() => {
  const distribution: Record<string, number> = {
    whisper: 0,
    echo: 0,
    resonance: 0,
    thunder: 0
  }
  
  wordProgress.value.forEach(word => {
    distribution[word.relicType] = (distribution[word.relicType] || 0) + 1
  })
  
  return distribution
})

const recentSessions = ref([
  {
    id: '1',
    date: new Date(),
    wordsPracticed: 10,
    completed: true
  },
  {
    id: '2',
    date: new Date(Date.now() - 24 * 60 * 60 * 1000),
    wordsPracticed: 8,
    completed: true
  },
  {
    id: '3',
    date: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000),
    wordsPracticed: 12,
    completed: true
  }
])

const getRelicTypeColor = (type: string) => {
  const colors: Record<string, string> = {
    whisper: 'gray',
    echo: 'blue',
    resonance: 'purple',
    thunder: 'red'
  }
  return colors[type] || 'gray'
}

const getRelicTypeTextColor = (type: string) => {
  const colors: Record<string, string> = {
    whisper: 'text-gray-600',
    echo: 'text-blue-600',
    resonance: 'text-purple-600',
    thunder: 'text-red-600'
  }
  return colors[type] || 'text-gray-600'
}

const getMasteryColor = (mastery: number) => {
  if (mastery >= 0.8) return 'green'
  if (mastery >= 0.5) return 'blue'
  if (mastery >= 0.3) return 'yellow'
  return 'gray'
}

const formatDate = (date: Date) => {
  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  }).format(date)
}

useHead({
  title: 'Legend Ledger - Palabam'
})
</script>

