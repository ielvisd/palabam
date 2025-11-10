# Palabam: AI-Powered Vocabulary Odyssey for Middle School Mastery

**Organization:** Flourish Schools  
**Project ID:** JnGyV0Xlx2AEiL31nu7J_1761523676397  
**Version:** 1.6 (Final – Cursor-Ready + PNPM Monorepo)  
**Date:** November 10, 2025

---

## 1. Executive Summary

Palabam is the explosive AI game that turns middle school vocabulary gaps into **multiplayer 3D raids** — now **powered by a scientifically proven spaced repetition engine** and **advanced TresJS with Cientos**. Students complete **10-minute daily sessions** that blend **new word introduction** with **timed reviews** of past relics, ensuring long-term retention.

- **No grade labels** — words scale via **Story Spark** (narrative profiling).
- Works for **2-year-olds** ("big bunny") to **adults** ("perspicacious") — same engine.
- Outshines Quizlet 10x: **3D immersion + voice + AI narrative + spaced repetition > flashcards**.
- **MCP-powered dev**: Cursor uses live Nuxt UI, Supabase, and AWS docs for flawless builds.
- **TresJS Inspiration**: Draws from proven patterns like interactive 3D courts (Agorespace) for immersive realms, Aviator game repo for quest loops, and Cientos for clickable relics and animations.

---

## 2. Problem Statement

Middle schoolers lack personalized, engaging vocab growth. Teachers waste hours on manual gap analysis. Existing tools (Quizlet) are 2D, generic, and drill-based — not story-driven, voice-inclusive, **or backed by spaced repetition science**.

---

## 3. Goals & Success Metrics

| Goal | Success Metric |
|------|----------------|
| Automate gap detection | 15–25% increase in novel word usage over 4 weeks |
| Provide personalized recommendations | 80%+ of recommendations rated "useful" by educators |
| Reduce teacher workload | 50% reduction in manual analysis time (survey) |
| Increase student engagement | 5x average session length vs. Quizlet |
| **Ensure long-term retention** | **70%+ recall after 30 days (spaced repetition benchmark)** |

---

## 4. Target Users & Personas

**Primary Users: Middle School Educators**

- **Persona: Ms. Rivera, 7th-Grade ELA Teacher**
  - Manages 120 students across 5 classes; tech-savvy but time-strapped.
  - Needs: Efficient tools to analyze and recommend vocabulary; desire to enhance student skills without manual effort.

**Secondary Users: Middle School Students**

- **Persona: Alex, 12-Year-Old 6th Grader**
  - Enjoys gamified apps; uses school iPad daily.
  - Needs: Personalized, challenging yet achievable vocabulary; support in improving language proficiency.

**Universal Adapters (Scalability):**

- **Niece (2yo)**: Sensory basics via voice and plush visuals.
- **Adult Learner**: Fancy vocabulary (e.g., SAT, professional writing) via advanced relic themes.

---

## 5. User Stories

- As a middle school educator, I want to receive a list of vocabulary words tailored to each student's proficiency level so that I can efficiently enhance their language skills.
- As a middle school student, I want to be challenged with new vocabulary words that I can realistically learn and use effectively, so that I can improve my language proficiency.
- As a student, I want to **tap "Start Session"** and complete a **10-minute vocab drill** that mixes **new words and timed reviews**.
- As a student, I want to **see basic progress** (e.g., "3/5 mastered") after each activity.
- As a teacher, I want to **deploy a session** and instantly see **who's mastering what** in a visual dashboard.
- As a parent, I want a **shareable link** to view my child's **legend ledger** and celebrate wins.

---

## 6. Functional Requirements

### P0: Must-have

- **Story Spark Profiling**
  - Voice/text input (e.g., "Tell me about your weekend") → transcribed → analyzed via spaCy/NLTK → scored against COCA/Lexile corpora → generates **relic resonance profile**.
  - No grade labels; words abstracted as "whisper relics" (basic) to "thunder relics" (advanced).
- **Relic Resonance Engine**
  - Suggests 5–7 ZPD-balanced words (70–80% learnability) as **3D artifacts** (TresJS with Cientos helpers for interactions).
  - Dynamic pacing: Mastery → evolution (e.g., "big" → "enormous").
- **Spaced Repetition System (SRS)**
  - **Algorithm**: SM-2 inspired (ease factor, interval, due date)
  - **Session Flow**:
    1. Tap **"Start Session"**
    2. 10-minute drill: **4 new words + 6–8 reviews** (timed)
    3. End with **basic progress display**
  - **Core Activities (6 total)**:
    1. **Flashcard Introduction**
       - Word + definition + example sentence
       - Voice: TTS reads; Student repeats
    2. **Meaning Multiple Choice**
       - 4 options; 1 correct
       - Voice: "Tap the meaning of *resilient*"
    3. **Dictated Spelling**
       - Hear word → type it
       - Voice: "Spell *resilient*"
    4. **Context Fill-in-the-Blank**
       - Sentence with gap
       - Voice: "Complete: The team was ___ after the loss."
    5. **Synonym/Antonym Selection**
       - 4 options; label as "same" or "opposite"
    6. **Sentence Generation**
       - Prompt: "Use *resilient* in a sentence about your day."
       - AI scores (grammar, relevance)
- **Dynamic Quest Generation**
  - Personalized raids (e.g., **Resilient Raid**) based on transcript themes (soccer → teamwork).
  - Full skill coverage: spelling, writing, speaking, reading, etymology.
- **Dual Input Modes**
  - **Voice**: Web Speech API (client) + AWS Transcribe fallback (noisy rooms).
  - **Text**: Typing, drag-and-drop, emoji responses.
  - Toggle via Nuxt UI `<USwitch>`.
- **Multiplayer Sync**
  - 2–8 players via Supabase Realtime.
  - Shared relic fusion (e.g., basic + advanced = hybrid tower).

### P1: Should-have

- **Teacher Dashboard**
  - Nuxt UI: Deploy sessions, view resonance meters, export reports (CSV/PDF).
  - Parent share links: `palab.am/student/abc?share=parent`.
- **PWA Support**
  - Mobile-ready out of the box (Nuxt auto-generates manifest).
- **Progress Export**
  - One-click lesson plans, IEP notes, parent summaries.

### P2: Nice-to-have

- **Procedural 3D Relics**
  - TresJS geometry generation (e.g., icosahedrons morphing by word length).
- **Voice Feedback via AWS Transcribe**
  - Pronunciation scoring, prosody boosts.
- **Parent Portal**
  - Full login, progress history (stretch goal).

---

## 7. Non-Functional Requirements

- **Performance**:
  - Session load <3s
  - <10k triangles per 3D model
  - Parallel processing of 100+ transcripts in <5 min
- **Scalability**:
  - 1,000+ concurrent users
  - Auto-scale on Vercel + AWS
- **Security**:
  - FERPA-compliant
  - Anonymized voice transcripts
  - Supabase Row Level Security (RLS)
- **Reliability**:
  - 99% uptime
  - Error handling for malformed inputs
- **Accessibility**:
  - WCAG 2.1 AA
  - Voice fallback, high contrast, screen reader support
  - **Age-appropriate UI**: Large buttons, simple fonts, plush visuals for toddlers

---

## 8. User Experience & Design Considerations

- **Workflows**:
  1. **Story Spark** → 2. **Daily Session (10 min)** → 3. **Quest Raid** → 4. **Legend Ledger** → 5. **Next Evolution**
- **Interface Principles**:
  - Clear visualization: Resonance meters, relic glows, progress timelines
  - Nuxt UI components: `<UProgress>`, `<UConfetti>`, `<UTimeline>`, `<UButton size="xl">`
  - **Basic Progress Display**: "3/5 mastered" + streak counter
- **Accessibility Needs**:
  - Voice/text toggle
  - Colorblind-safe palettes
  - Large tap targets for toddlers
  - **Age-appropriate UI**:
    - **Toddlers**: Plush animals, big buttons, voice-only
    - **Middle School**: 3D realms, multiplayer
    - **Adults**: Clean, dark mode, advanced themes

---

## 9. Technical Requirements

### System Architecture

- **Cloud-based deployment**
  - **Frontend**: Vercel
  - **Backend**: AWS Lambda (via Supabase Edge Functions or direct)
  - **Database/Auth/Realtime**: Supabase
  - **Voice Fallback**: AWS Transcribe (MCP-wired)

### Monorepo Structure

```
palabam/
├── backend/                  # FastAPI
│   ├── main.py
│   ├── nlp/
│   │   ├── profiler.py
│   │   ├── recommender.py
│   │   └── srs.py           # SM-2 logic
│   └── requirements.txt
├── frontend/                 # Nuxt 3
│   ├── app.vue
│   ├── pages/
│   │   ├── index.vue
│   │   ├── spark.vue
│   │   ├── session.vue      # 10-min drill
│   │   └── games/raid.vue
│   ├── composables/
│   │   ├── useVocabInput.ts
│   │   ├── useSRS.ts
│   │   └── useProceduralRelic.ts
│   ├── assets/css/tailwind.css
│   └── nuxt.config.ts
├── supabase/
│   └── migrations/
└── pnpm-workspace.yaml
```

### Package Manager

- **PNPM** — **No npm**.
  - Faster, disk-efficient, strict dependency hoisting.
  - Required for monorepo with `/frontend` + `/backend`.
  - Cursor auto-detects `pnpm-lock.yaml`.

#### Root Setup

```yaml
# pnpm-workspace.yaml
packages:
  - 'frontend'
  - 'backend'
```

```bash
# Install PNPM
corepack enable
corepack prepare pnpm@latest --activate

# Install deps
pnpm install
```

#### Frontend (`frontend/package.json`)

```bash
pnpm add @nuxt/ui tresjs @supabase/nuxt @tresjs/cientos
pnpm add -D tailwindcss
pnpm exec tailwindcss init
```

#### Backend (`backend/requirements.txt`)

```txt
fastapi
uvicorn
spacy
nltk
scikit-learn
boto3
```

#### CSS Setup (`frontend/assets/css/tailwind.css`)

```css
@import "tailwindcss";
@import "@nuxt/ui";
```

#### Frontend Config (`frontend/nuxt.config.ts`)

```ts
export default defineNuxtConfig({
  modules: ['@nuxt/ui', '@supabase/nuxt'],
  css: ['~/assets/css/tailwind.css'],
  supabase: {
    redirectOptions: {
      login: '/login',
      callback: '/confirm'
    }
  }
})
```

#### Tailwind Config (`tailwind.config.js`)

```js
export default {
  content: [
    './components/**/*.{js,vue,ts}',
    './layouts/**/*.vue',
    './pages/**/*.vue',
    './plugins/**/*.{js,ts}',
    './nuxt.config.{js,ts}',
    './app.vue'
  ]
}
```

### 3D Assets & TresJS Integration

- **poly.pizza**: Free CC-BY low-poly GLTF models (crystals, fortresses, orbs)
- **Procedural**: TresJS IcosahedronGeometry, CylinderGeometry
- **Performance**: <5k tris per model, lazy-loaded

#### TresJS Enhancements

- **Core API**: Use primitives like `<TresMesh>`, `<TresIcosahedronGeometry>` for relic artifacts; event handling via Vue composables (e.g., `@click` on meshes for interactions).
- **Nuxt patterns**: Wrap in `<TresCanvas>` with dynamic props.
- **Cookbook Inspiration**: Leverage recipes for animations (e.g., GSAP for relic morphs), OrbitControls for quest navigation, and model loading for poly.pizza imports.
- **Cientos Package**: Advanced helpers for interactions (e.g., `<OrbitControls>` for relic inspection), effects (e.g., text animations for sentence generation), and morph targets (voice-synced relic changes).

**Install**: `pnpm add @tresjs/cientos`

**Example**:

```vue
<script setup>
import { OrbitControls } from '@tresjs/cientos'
</script>
<template>
  <TresCanvas>
    <TresMesh> <!-- Relic -->
      <TresIcosahedronGeometry :args="[1, 1]" />
      <TresMeshStandardMaterial color="#00ff88" />
    </TresMesh>
    <OrbitControls /> <!-- Clickable inspection -->
  </TresCanvas>
</template>
```

- **Repo Inspiration**: From "tres-the-aviator" GitHub: Adopt game loop patterns (e.g., update cycles for SRS timers), user input handling (keyboard/voice for activities), and scene management for raid flows. Structure: Modular components for quests, reusable for multiplayer sync.
- **Demo Inspiration**: Agorespace 3D courts showcase immersive sports visualizations—adapt for Palabam realms (e.g., soccer-themed bastions with dynamic lighting on mastery, procedural turf for context quests, user panning for relic exploration).

### MCP Setup (Dev Superpower)

```bash
# Frontend
pnpm dlx nuxi module add nuxt-mcp
pnpm add @nuxt/ui @tresjs/cientos

# Backend
pip install aws-mcp-proxy
```

#### Cursor Rules (`.cursor/rules.md`)

```md
Use Nuxt UI MCP for components.
Use Supabase MCP for realtime/auth.
Use AWS MCP for Transcribe/Lambda.
Never use npm — use pnpm only.
All 3D from poly.pizza or procedural TresJS + Cientos.
No grade labels — use "relic resonance".
Implement 10-minute SRS sessions with 6 core activities.
Reference TresJS cookbook for animations, Cientos for interactions.
```

---

## 10. Dependencies & Assumptions

- Availability of student conversation transcripts and writing samples (via Story Spark).
- Integration with Google Classroom (fallback to manual input).
- Access to Vercel, Supabase, AWS (free tier for dev).
- MCP servers running locally during dev (Nuxt UI on port 3100; AWS via proxy).
- Cursor Pro for full MCP client support.

---

## 11. Out of Scope

- Direct classroom implementation or educator training.
- Development of proprietary AI frameworks.
- Real-time speech-to-text conversion (assumes Web Speech API + Transcribe).
- Mobile app (PWA covers it).
- Parent portal login (share links only).

---

## 12. Pedagogical Foundation

All recommendations incorporate evidence-based routines:

| Practice | Implementation in Palabam |
|----------|---------------------------|
| Explicit Word Selection | 8–10 high-utility words/week; student-friendly defs + examples |
| Frayer Model | 3D rotatable relic with 4 facets (def, char, ex, non-ex) |
| Semantic Mapping | TresJS web of synonyms/antonyms/contexts |
| Morphemic Analysis | Root raids (e.g., "re-" + "silio" = leap back) |
| Repeated Review | Spaced repetition (SM-2) in 10-min sessions |
| Multimodal Practice | 6 core activities covering spelling, meaning, context, usage |

**Alignment**: National Reading Panel, Beck et al. (2002), WWC (2011), Hirsch (2006), Anki/SRS research

---

## 13. 10-Minute Session Flow (`pages/session.vue` stub)

```vue
<script setup lang="ts">
const activities = [
  'flashcard', 'multiple-choice', 'spelling', 
  'fill-blank', 'synonym', 'sentence'
]
const progress = ref(0)
const total = ref(10) // 4 new + 6 reviews
</script>

<template>
  <UContainer class="p-6">
    <UCard>
      <template #header>
        <h2 class="text-2xl font-bold">Daily Vocab Drill</h2>
        <UProgress :value="progress" :max="total" class="mt-2" />
      </template>
      
      <UButton size="xl" @click="startSession" class="w-full">
        Start Session
      </UButton>
    </UCard>
  </UContainer>
</template>
```

---

## 14. Resilient Raid MVP (`pages/games/raid.vue` stub)

```vue
<script setup lang="ts">
import { TresCanvas } from '@tresjs/core'
import { OrbitControls } from '@tresjs/cientos'
import { useVocabInput } from '@/composables/useVocabInput'
import { useProceduralRelic } from '@/composables/useProceduralRelic'

const { isVoiceMode } = useVocabInput()
const { mesh: orb } = useProceduralRelic('resilient')
</script>

<template>
  <UContainer>
    <TresCanvas>
      <TresScene>
        <primitive :object="orb" />
        <OrbitControls /> <!-- Cientos for relic interaction -->
      </TresScene>
    </TresCanvas>
    <USwitch v-model="isVoiceMode" label="Voice Mode" />
  </UContainer>
</template>
```
