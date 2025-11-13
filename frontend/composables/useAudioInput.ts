/**
 * useAudioInput composable
 * Lightweight voice input for text fields with real-time transcription
 */
export const useAudioInput = () => {
  const isRecording = ref(false)
  const transcript = ref('')
  const interimTranscript = ref('')
  const error = ref<string | null>(null)
  const recognition: Ref<SpeechRecognition | null> = ref(null)

  // Initialize Web Speech API
  const initSpeechRecognition = () => {
    if (typeof window === 'undefined') return null

    const SpeechRecognition = window.SpeechRecognition || (window as any).webkitSpeechRecognition
    
    if (!SpeechRecognition) {
      error.value = 'Speech recognition not supported in this browser'
      return null
    }

    const recognitionInstance = new SpeechRecognition()
    recognitionInstance.continuous = true
    recognitionInstance.interimResults = true
    recognitionInstance.lang = 'en-US'

    recognitionInstance.onresult = (event: SpeechRecognitionEvent) => {
      let interim = ''
      let final = ''

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const result = event.results[i]
        if (result.isFinal) {
          final += result[0].transcript
        } else {
          interim += result[0].transcript
        }
      }

      interimTranscript.value = interim
      if (final) {
        transcript.value += final + ' '
        interimTranscript.value = ''
      }
    }

    recognitionInstance.onerror = (event: SpeechRecognitionErrorEvent) => {
      error.value = `Speech recognition error: ${event.error}`
      isRecording.value = false
    }

    recognitionInstance.onend = () => {
      isRecording.value = false
    }

    return recognitionInstance
  }

  // Start recording
  const startRecording = async () => {
    error.value = null
    transcript.value = ''
    interimTranscript.value = ''

    if (!recognition.value) {
      recognition.value = initSpeechRecognition()
    }

    if (!recognition.value) {
      error.value = 'Speech recognition not available'
      return
    }

    try {
      isRecording.value = true
      recognition.value.start()
    } catch (err: any) {
      error.value = err.message || 'Failed to start recording'
      isRecording.value = false
    }
  }

  // Stop recording
  const stopRecording = () => {
    if (recognition.value && isRecording.value) {
      recognition.value.stop()
      isRecording.value = false
      // Append any remaining interim text
      if (interimTranscript.value) {
        transcript.value += interimTranscript.value + ' '
        interimTranscript.value = ''
      }
    }
  }

  // Clear transcript
  const clearTranscript = () => {
    transcript.value = ''
    interimTranscript.value = ''
  }

  // Get current transcript (including interim)
  const getCurrentTranscript = computed(() => {
    return transcript.value + (interimTranscript.value || '')
  })

  // Cleanup
  onUnmounted(() => {
    if (recognition.value) {
      recognition.value.stop()
    }
  })

  return {
    isRecording,
    transcript,
    interimTranscript,
    getCurrentTranscript,
    error,
    startRecording,
    stopRecording,
    clearTranscript
  }
}

// Type definitions
interface SpeechRecognition extends EventTarget {
  continuous: boolean
  interimResults: boolean
  lang: string
  start(): void
  stop(): void
  abort(): void
  onresult: ((event: SpeechRecognitionEvent) => void) | null
  onerror: ((event: SpeechRecognitionErrorEvent) => void) | null
  onend: (() => void) | null
}

interface SpeechRecognitionEvent {
  results: SpeechRecognitionResultList
  resultIndex: number
}

interface SpeechRecognitionResultList {
  length: number
  item(index: number): SpeechRecognitionResult
  [index: number]: SpeechRecognitionResult
}

interface SpeechRecognitionResult {
  length: number
  item(index: number): SpeechRecognitionAlternative
  [index: number]: SpeechRecognitionAlternative
  isFinal: boolean
}

interface SpeechRecognitionAlternative {
  transcript: string
  confidence: number
}

interface SpeechRecognitionErrorEvent {
  error: string
  message: string
}

declare global {
  interface Window {
    SpeechRecognition: typeof SpeechRecognition
    webkitSpeechRecognition: typeof SpeechRecognition
  }
}

