/**
 * useProceduralRelic composable
 * Generates 3D relic artifacts using TresJS
 * Integrates Cientos helpers for interactions
 */
import { TresCanvas } from '@tresjs/core'
import { OrbitControls } from '@tresjs/cientos'
import { IcosahedronGeometry, MeshStandardMaterial, Color } from 'three'

export type RelicType = 'whisper' | 'echo' | 'resonance' | 'thunder'

interface RelicConfig {
  word: string
  relicType: RelicType
  mastery?: number
  glowIntensity?: number
}

const RELIC_COLORS: Record<RelicType, string> = {
  whisper: '#E0E7FF', // Light blue
  echo: '#A5B4FC', // Medium blue
  resonance: '#6366F1', // Indigo
  thunder: '#4F46E5' // Deep indigo
}

const RELIC_SIZES: Record<RelicType, number> = {
  whisper: 0.8,
  echo: 1.0,
  resonance: 1.2,
  thunder: 1.5
}

export const useProceduralRelic = (config: RelicConfig) => {
  const { word, relicType, mastery = 0, glowIntensity = 1.0 } = config

  // Create geometry based on word length and relic type
  const geometry = computed(() => {
    const baseSize = RELIC_SIZES[relicType]
    const wordLength = word.length
    // Adjust size slightly based on word length
    const size = baseSize + (wordLength * 0.05)
    
    return new IcosahedronGeometry(size, 1)
  })

  // Create material with color and glow effect
  const material = computed(() => {
    const baseColor = new Color(RELIC_COLORS[relicType])
    
    // Adjust brightness based on mastery
    const masteryBoost = mastery * 0.3
    baseColor.multiplyScalar(1.0 + masteryBoost)
    
    const mat = new MeshStandardMaterial({
      color: baseColor,
      emissive: baseColor,
      emissiveIntensity: glowIntensity * (0.2 + mastery * 0.3),
      metalness: 0.3 + mastery * 0.2,
      roughness: 0.7 - mastery * 0.2
    })
    
    return mat
  })

  // Create mesh
  const mesh = computed(() => {
    const relicMesh = new (window as any).THREE.Mesh(geometry.value, material.value)
    
    // Add word as userData for reference
    relicMesh.userData = {
      word,
      relicType,
      mastery
    }
    
    return relicMesh
  })

  // Animation function for relic glow
  const animateGlow = (mesh: any, time: number) => {
    if (!mesh || !mesh.material) return
    
    const pulse = Math.sin(time * 2) * 0.1 + 0.9
    mesh.material.emissiveIntensity = glowIntensity * (0.2 + mastery * 0.3) * pulse
    
    // Slight rotation
    mesh.rotation.y += 0.01
    mesh.rotation.x += 0.005
  }

  // Get relic color for UI display
  const relicColor = computed(() => RELIC_COLORS[relicType])

  // Get relic size for UI
  const relicSize = computed(() => RELIC_SIZES[relicType])

  return {
    mesh,
    geometry,
    material,
    relicType,
    relicColor,
    relicSize,
    animateGlow,
    word
  }
}

/**
 * Create multiple relics for a word list
 */
export const useRelicCollection = (words: Array<{ word: string; relicType: RelicType; mastery?: number }>) => {
  const relics = words.map(wordData => 
    useProceduralRelic({
      word: wordData.word,
      relicType: wordData.relicType,
      mastery: wordData.mastery || 0
    })
  )

  return {
    relics,
    getRelicByWord: (word: string) => {
      return relics.find(r => r.word === word)
    }
  }
}

