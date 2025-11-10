/**
 * useStorySpark composable
 * Enhanced voice input with real-time transcription and record-then-transcribe modes
 */
export const useStorySpark = () => {
  const isVoiceMode = ref(false)
  const isRecording = ref(false)
  const isRealTimeMode = ref(true) // Toggle between real-time and record modes
  const transcript = ref('')
  const interimTranscript = ref('') // For real-time display
  const error = ref<string | null>(null)
  const recognition: Ref<SpeechRecognition | null> = ref(null)
  const mediaRecorder: Ref<MediaRecorder | null> = ref(null)
  const audioChunks: Ref<Blob[]> = ref([])

  // Initialize Web Speech API with real-time support
  const initSpeechRecognition = (realTime: boolean = true) => {
    if (typeof window === 'undefined') return null

    const SpeechRecognition = window.SpeechRecognition || (window as any).webkitSpeechRecognition
    
    if (!SpeechRecognition) {
      error.value = 'Speech recognition not supported in this browser'
      return null
    }

    const recognitionInstance = new SpeechRecognition()
    recognitionInstance.continuous = realTime // Continuous for real-time, false for record mode
    recognitionInstance.interimResults = realTime // Show interim results for real-time
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

      if (realTime) {
        interimTranscript.value = interim
        if (final) {
          transcript.value += final + ' '
          interimTranscript.value = ''
        }
      } else {
        // Record mode - only update on final result
        transcript.value = final
        isRecording.value = false
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

  // Start real-time transcription
  const startRealTimeRecording = async () => {
    if (!isVoiceMode.value) {
      error.value = 'Voice mode is not enabled'
      return
    }

    error.value = null
    transcript.value = ''
    interimTranscript.value = ''

    if (!recognition.value) {
      recognition.value = initSpeechRecognition(true)
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

  // Start record-then-transcribe mode
  const startRecordMode = async () => {
    if (!isVoiceMode.value) {
      error.value = 'Voice mode is not enabled'
      return
    }

    error.value = null
    transcript.value = ''
    audioChunks.value = []

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const recorder = new MediaRecorder(stream)
      mediaRecorder.value = recorder

      recorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunks.value.push(event.data)
        }
      }

      recorder.onstop = async () => {
        const audioBlob = new Blob(audioChunks.value, { type: 'audio/webm' })
        await transcribeRecordedAudio(audioBlob)
        
        // Stop all tracks
        stream.getTracks().forEach(track => track.stop())
      }

      isRecording.value = true
      recorder.start()
    } catch (err: any) {
      error.value = err.message || 'Failed to access microphone'
      isRecording.value = false
    }
  }

  // Transcribe recorded audio using Web Speech API
  const transcribeRecordedAudio = async (audioBlob: Blob) => {
    try {
      // For now, use Web Speech API (in production, could use AWS Transcribe)
      // Create audio element and play it, then use speech recognition
      // This is a simplified approach - in production, send to backend for AWS Transcribe
      
      const config = useRuntimeConfig()
      const apiUrl = config.public.apiUrl || 'http://localhost:8000'
      
      const formData = new FormData()
      formData.append('audio', audioBlob, 'audio.webm')

      const response = await $fetch(`${apiUrl}/api/transcribe`, {
        method: 'POST',
        body: formData
      })

      transcript.value = (response as any).transcript || ''
    } catch (err: any) {
      // Fallback: try Web Speech API directly
      console.warn('Backend transcription failed, using Web Speech API')
      
      if (!recognition.value) {
        recognition.value = initSpeechRecognition(false)
      }
      
      if (recognition.value) {
        try {
          isRecording.value = true
          recognition.value.start()
          // Note: This is a workaround - Web Speech API doesn't directly support audio blobs
          // In production, use AWS Transcribe for recorded audio
        } catch (e) {
          error.value = 'Transcription failed. Please try typing instead.'
        }
      } else {
        error.value = 'Transcription not available. Please try typing instead.'
      }
    }
  }

  // Stop recording
  const stopRecording = () => {
    if (isRealTimeMode.value) {
      // Real-time mode
      if (recognition.value && isRecording.value) {
        recognition.value.stop()
        isRecording.value = false
        // Append any remaining interim text
        if (interimTranscript.value) {
          transcript.value += interimTranscript.value + ' '
          interimTranscript.value = ''
        }
      }
    } else {
      // Record mode
      if (mediaRecorder.value && isRecording.value) {
        mediaRecorder.value.stop()
        isRecording.value = false
      }
    }
  }

  // Toggle between real-time and record modes
  const toggleTranscriptionMode = () => {
    if (isRecording.value) {
      stopRecording()
    }
    isRealTimeMode.value = !isRealTimeMode.value
  }

  // Toggle between voice and text mode
  const toggleInputMode = () => {
    isVoiceMode.value = !isVoiceMode.value
    
    if (!isVoiceMode.value && isRecording.value) {
      stopRecording()
    }
  }

  // Start recording based on current mode
  const startRecording = () => {
    if (isRealTimeMode.value) {
      startRealTimeRecording()
    } else {
      startRecordMode()
    }
  }

  // Get display transcript (includes interim for real-time)
  const displayTranscript = computed(() => {
    if (isRealTimeMode.value && interimTranscript.value) {
      return transcript.value + interimTranscript.value
    }
    return transcript.value
  })

  // Cleanup
  onUnmounted(() => {
    if (recognition.value) {
      recognition.value.stop()
    }
    if (mediaRecorder.value) {
      mediaRecorder.value.stop()
    }
  })

  return {
    isVoiceMode,
    isRecording,
    isRealTimeMode,
    transcript,
    interimTranscript,
    displayTranscript,
    error,
    startRecording,
    stopRecording,
    toggleInputMode,
    toggleTranscriptionMode
  }
}

// Type definitions (reuse from useVocabInput)
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

