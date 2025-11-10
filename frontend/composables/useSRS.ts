/**
 * useSRS composable
 * Handles Spaced Repetition System (SRS) operations
 * Fetches due words and updates progress
 */

export interface Word {
  id: string
  word: string
  definition: string
  example?: string
  relic_type?: string
  difficulty_score?: number
}

export interface SRSProgress {
  ease_factor: number
  interval: number
  repetitions: number
  due_date: string
  mastery_level: number
}

export interface DueWordsResponse {
  new_words: Word[]
  review_words: Word[]
}

export const useSRS = () => {
  const loading = ref(false)
  const error = ref<string | null>(null)
  const sessionWords = ref<Word[]>([])
  const progress = ref<Map<string, SRSProgress>>(new Map())

  /**
   * Fetch words due for review and new words for session
   */
  const fetchDueWords = async (
    studentId: string,
    newCount: number = 4,
    reviewCount: number = 8
  ): Promise<DueWordsResponse> => {
    loading.value = true
    error.value = null

    try {
      const response = await $fetch<DueWordsResponse>('/api/srs/due-words', {
        method: 'POST',
        body: {
          student_id: studentId,
          new_count: newCount,
          review_count: reviewCount
        }
      })

      // Combine new and review words for session
      sessionWords.value = [...response.new_words, ...response.review_words]

      return response
    } catch (err: any) {
      error.value = err.message || 'Failed to fetch due words'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Update SRS progress after completing an activity
   */
  const updateProgress = async (
    studentId: string,
    wordId: string,
    quality: number // 0-5 scale
  ): Promise<SRSProgress> => {
    loading.value = true
    error.value = null

    try {
      const response = await $fetch<SRSProgress>('/api/srs/update', {
        method: 'POST',
        body: {
          student_id: studentId,
          word_id: wordId,
          quality
        }
      })

      // Update local progress map
      progress.value.set(wordId, response)

      return response
    } catch (err: any) {
      error.value = err.message || 'Failed to update progress'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Get mastery level for a word
   */
  const getMasteryLevel = (wordId: string): number => {
    return progress.value.get(wordId)?.mastery_level || 0
  }

  /**
   * Check if word is mastered (mastery >= 0.8)
   */
  const isMastered = (wordId: string): boolean => {
    return getMasteryLevel(wordId) >= 0.8
  }

  /**
   * Get progress statistics
   */
  const getProgressStats = () => {
    const total = sessionWords.value.length
    const mastered = sessionWords.value.filter(w => isMastered(w.id)).length
    const inProgress = total - mastered

    return {
      total,
      mastered,
      inProgress,
      masteryPercentage: total > 0 ? (mastered / total) * 100 : 0
    }
  }

  /**
   * Reset session data
   */
  const resetSession = () => {
    sessionWords.value = []
    progress.value.clear()
  }

  return {
    loading,
    error,
    sessionWords,
    progress,
    fetchDueWords,
    updateProgress,
    getMasteryLevel,
    isMastered,
    getProgressStats,
    resetSession
  }
}

