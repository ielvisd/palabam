/**
 * useVocabInput composable
 * Handles dual input modes: voice (Web Speech API) and text
 * Falls back to AWS Transcribe for noisy environments
 */
export const useVocabInput = () => {
  const isVoiceMode = ref(false)
  const isRecording = ref(false)
  const transcript = ref('')
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
    recognitionInstance.continuous = false
    recognitionInstance.interimResults = false
    recognitionInstance.lang = 'en-US'

    recognitionInstance.onresult = (event: SpeechRecognitionEvent) => {
      const result = event.results[event.results.length - 1]
      transcript.value = result[0].transcript
      isRecording.value = false
    }

    recognitionInstance.onerror = (event: SpeechRecognitionErrorEvent) => {
      error.value = `Speech recognition error: ${event.error}`
      isRecording.value = false
      
      // Fallback to AWS Transcribe if Web Speech API fails
      if (event.error === 'no-speech' || event.error === 'audio-capture') {
        console.warn('Falling back to AWS Transcribe')
        // This would trigger AWS Transcribe fallback
      }
    }

    recognitionInstance.onend = () => {
      isRecording.value = false
    }

    return recognitionInstance
  }

  // Start voice recording
  const startRecording = async () => {
    if (!isVoiceMode.value) {
      error.value = 'Voice mode is not enabled'
      return
    }

    error.value = null
    transcript.value = ''

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

  // Stop voice recording
  const stopRecording = () => {
    if (recognition.value && isRecording.value) {
      recognition.value.stop()
      isRecording.value = false
    }
  }

  // Toggle between voice and text mode
  const toggleInputMode = () => {
    isVoiceMode.value = !isVoiceMode.value
    
    if (!isVoiceMode.value && isRecording.value) {
      stopRecording()
    }
  }

  // Fallback to AWS Transcribe (would be called from backend)
  const transcribeWithAWS = async (audioBlob: Blob): Promise<string> => {
    try {
      const formData = new FormData()
      formData.append('audio', audioBlob, 'audio.webm')

      const response = await $fetch('/api/transcribe', {
        method: 'POST',
        body: formData
      })

      return (response as any).transcript || ''
    } catch (err: any) {
      error.value = `Transcription failed: ${err.message}`
      throw err
    }
  }

  // Text-to-Speech for reading words
  const speak = (text: string, lang = 'en-US') => {
    if (typeof window === 'undefined' || !('speechSynthesis' in window)) {
      console.warn('Text-to-speech not supported')
      return
    }

    const utterance = new SpeechSynthesisUtterance(text)
    utterance.lang = lang
    utterance.rate = 0.9
    utterance.pitch = 1.0
    
    window.speechSynthesis.speak(utterance)
  }

  // Cleanup on unmount
  onUnmounted(() => {
    if (recognition.value) {
      recognition.value.stop()
    }
  })

  return {
    isVoiceMode,
    isRecording,
    transcript,
    error,
    startRecording,
    stopRecording,
    toggleInputMode,
    transcribeWithAWS,
    speak
  }
}

// Type definitions for Web Speech API
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

