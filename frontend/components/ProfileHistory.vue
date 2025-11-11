<template>
  <div class="space-y-4">
    <div v-if="title" class="flex items-center justify-between mb-4">
      <h3 class="font-semibold text-lg text-navy dark:text-white">{{ title }}</h3>
      <UBadge v-if="profiles.length > 0" color="primary" variant="soft" size="sm">
        {{ profiles.length }} {{ profiles.length === 1 ? 'profile' : 'profiles' }}
      </UBadge>
    </div>

    <div v-if="loading" class="text-center py-8">
      <UIcon name="i-heroicons-arrow-path" class="animate-spin text-4xl text-primary mb-2" />
      <p class="text-sm text-gray-600 dark:text-gray-400">Loading profile history...</p>
    </div>

    <div v-else-if="profiles.length === 0" class="text-center py-8 bg-gray-50 dark:bg-gray-800 rounded-lg">
      <UIcon name="i-heroicons-document-text" class="text-4xl text-gray-400 dark:text-gray-500 mb-3" />
      <p class="text-gray-600 dark:text-gray-300">No profile history yet.</p>
      <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">Profiles will appear here after transcripts are analyzed.</p>
    </div>

    <UTimeline v-else :items="timelineItems" class="w-full">
      <template #description="{ item }">
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm mt-2">
          <div>
            <p class="text-gray-600 dark:text-gray-400">Unique Words</p>
            <p class="font-semibold text-gray-900 dark:text-white">
              {{ item.unique_words || 0 }}
            </p>
          </div>
          <div>
            <p class="text-gray-600 dark:text-gray-400">Total Words</p>
            <p class="font-semibold text-gray-900 dark:text-white">
              {{ item.total_words || 0 }}
            </p>
          </div>
          <div>
            <p class="text-gray-600 dark:text-gray-400">Complexity</p>
            <p class="font-semibold text-gray-900 dark:text-white">
              {{ Math.round((item.complexity_score || 0) * 100) }}%
            </p>
          </div>
          <div>
            <p class="text-gray-600 dark:text-gray-400">Lexical Diversity</p>
            <p class="font-semibold text-gray-900 dark:text-white">
              {{ Math.round((item.lexical_diversity || 0) * 100) }}%
            </p>
          </div>
        </div>
        <div v-if="showActions" class="mt-3">
          <UButton
            v-if="onProfileClick"
            @click="handleProfileClick(item.profile)"
            variant="ghost"
            color="primary"
            size="xs"
            icon="i-heroicons-arrow-right"
          >
            View Details
          </UButton>
        </div>
      </template>
    </UTimeline>
  </div>
</template>

<script setup lang="ts">
interface Profile {
  id: string
  created_at: string
  vocabulary_level?: string
  resonance_data?: {
    vocabulary_level?: string
    unique_words?: number
    total_words?: number
    complexity_score?: number
    lexical_diversity?: number
  }
}

interface Props {
  profiles?: Profile[]
  studentId?: string
  title?: string
  loading?: boolean
  showActions?: boolean
  limit?: number
}

const props = withDefaults(defineProps<Props>(), {
  profiles: () => [],
  title: 'Profile History',
  loading: false,
  showActions: true,
  limit: undefined
})

const emit = defineEmits<{
  profileClick: [profile: Profile]
}>()

const getLevelColor = (level?: string) => {
  const colors: Record<string, string> = {
    'K-1': 'primary',
    '2-3': 'primary',
    '4-5': 'teal',
    '6-7': 'teal',
    '8-9': 'yellow',
    '10-11': 'yellow',
    '12+': 'pink',
    beginner: 'primary',
    intermediate: 'teal',
    advanced: 'yellow',
    expert: 'pink'
  }
  return colors[level || ''] || 'gray'
}

const formatDate = (dateString?: string | null) => {
  if (!dateString) return 'Unknown date'
  try {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch {
    return dateString
  }
}

const timelineItems = computed(() => {
  let profilesToShow = props.profiles
  
  if (props.limit && props.limit > 0) {
    profilesToShow = profilesToShow.slice(0, props.limit)
  }
  
  return profilesToShow.map((profile) => {
    const vocabLevel = profile.vocabulary_level || profile.resonance_data?.vocabulary_level
    const resonanceData = profile.resonance_data || {}
    
    return {
      date: formatDate(profile.created_at),
      title: vocabLevel ? `Vocabulary Level: ${vocabLevel}` : 'Profile Analysis',
      description: '',
      icon: 'i-heroicons-document-check',
      profile: profile,
      unique_words: resonanceData.unique_words,
      total_words: resonanceData.total_words,
      complexity_score: resonanceData.complexity_score,
      lexical_diversity: resonanceData.lexical_diversity,
      vocabulary_level: vocabLevel
    }
  })
})

const onProfileClick = (profile: Profile) => {
  emit('profileClick', profile)
}

const handleProfileClick = (profile: Profile) => {
  onProfileClick(profile)
}
</script>

