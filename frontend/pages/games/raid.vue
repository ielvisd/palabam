<template>
  <div class="h-screen w-screen">
    <TresCanvas>
      <TresPerspectiveCamera :position="[0, 5, 10]" />
      <OrbitControls />
      
      <!-- Lighting -->
      <TresAmbientLight :intensity="0.5" />
      <TresDirectionalLight :position="[10, 10, 5]" :intensity="1" />
      
      <!-- Scene -->
      <TresScene>
        <!-- Procedural Relics -->
        <TresMesh
          v-for="(relic, index) in relics"
          :key="relic.word"
          :position="getRelicPosition(index)"
          @click="selectRelic(relic)"
        >
          <TresIcosahedronGeometry :args="[relicSize, 1]" />
          <TresMeshStandardMaterial
            :color="relic.relicColor"
            :emissive="relic.relicColor"
            :emissive-intensity="relic.mastery * 0.3"
            :metalness="0.3 + relic.mastery * 0.2"
            :roughness="0.7 - relic.mastery * 0.2"
          />
        </TresMesh>
        
        <!-- Ground Plane -->
        <TresMesh :rotation="[-Math.PI / 2, 0, 0]" :position="[0, -2, 0]">
          <TresPlaneGeometry :args="[20, 20]" />
          <TresMeshStandardMaterial color="#4a5568" />
        </TresMesh>
      </TresScene>
    </TresCanvas>

    <!-- UI Overlay -->
    <div class="absolute top-4 left-4 right-4 z-10">
      <UCard>
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-2xl font-bold">{{ questTheme }} Raid</h1>
            <p class="text-gray-600">Click on relics to start challenges</p>
          </div>
          <div class="flex gap-4">
            <UButton
              v-if="selectedRelic"
              @click="startChallenge"
              color="primary"
            >
              Start Challenge
            </UButton>
            <UButton
              to="/session"
              variant="outline"
            >
              Back to Session
            </UButton>
          </div>
        </div>
      </UCard>
    </div>

    <!-- Selected Relic Info -->
    <div v-if="selectedRelic" class="absolute bottom-4 left-4 right-4 z-10">
      <UCard>
        <div class="space-y-2">
          <h3 class="text-xl font-bold">{{ selectedRelic.word }}</h3>
          <p class="text-gray-600">{{ selectedRelic.definition }}</p>
          <div class="flex gap-2">
            <UBadge :color="getRelicTypeColor(selectedRelic.relicType)">
              {{ selectedRelic.relicType }}
            </UBadge>
            <UBadge color="blue">
              Mastery: {{ Math.round(selectedRelic.mastery * 100) }}%
            </UBadge>
          </div>
        </div>
      </UCard>
    </div>
  </div>
</template>

<script setup lang="ts">
import { TresCanvas, TresScene, TresPerspectiveCamera, TresAmbientLight, TresDirectionalLight, TresMesh, TresIcosahedronGeometry, TresPlaneGeometry, TresMeshStandardMaterial } from '@tresjs/core'
import { OrbitControls } from '@tresjs/cientos'
import { useProceduralRelic } from '@/composables/useProceduralRelic'
import { useMultiplayer } from '@/composables/useMultiplayer'

// Quest data
const questTheme = ref('Resilient')
const selectedRelic = ref<any>(null)

// Multiplayer
const { currentRoom, players, isConnected, joinRoom, shareRelicFusion } = useMultiplayer()

// Sample relics for the quest
const relicData = [
  {
    word: 'resilient',
    definition: 'able to recover quickly from difficulties',
    relicType: 'resonance' as const,
    mastery: 0.6
  },
  {
    word: 'perseverance',
    definition: 'persistence in doing something despite difficulty',
    relicType: 'thunder' as const,
    mastery: 0.3
  },
  {
    word: 'determined',
    definition: 'having made a firm decision',
    relicType: 'resonance' as const,
    mastery: 0.5
  }
]

// Create relics using composable
const relics = relicData.map(data => {
  const relic = useProceduralRelic({
    word: data.word,
    relicType: data.relicType,
    mastery: data.mastery
  })
  return {
    ...relic,
    definition: data.definition,
    mastery: data.mastery
  }
})

const relicSize = computed(() => {
  return 1.0
})

const getRelicPosition = (index: number) => {
  const angle = (index / relics.length) * Math.PI * 2
  const radius = 3
  return [
    Math.cos(angle) * radius,
    0,
    Math.sin(angle) * radius
  ]
}

const selectRelic = (relic: any) => {
  selectedRelic.value = relic
}

const startChallenge = () => {
  if (!selectedRelic.value) return
  
  // Navigate to challenge or show challenge modal
  // For now, just log
  console.log('Starting challenge for:', selectedRelic.value.word)
  
  // TODO: Implement challenge flow
  // This would show different challenge types based on quest theme
}

const getRelicTypeColor = (type: string) => {
  const colors: Record<string, string> = {
    whisper: 'gray',
    echo: 'blue',
    resonance: 'purple',
    thunder: 'red'
  }
  return colors[type] || 'gray'
}

useHead({
  title: 'Quest Raid - Palabam'
})
</script>

<style scoped>
/* Ensure canvas takes full screen */
:deep(.tres-canvas) {
  width: 100%;
  height: 100%;
}
</style>

