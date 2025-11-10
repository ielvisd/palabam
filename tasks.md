# Palabam Project Tasks

## Project Setup

- [ ] Initialize PNPM monorepo with `pnpm-workspace.yaml`
- [ ] Set up `frontend/` directory structure (Nuxt 3)
- [ ] Set up `backend/` directory structure (FastAPI)
- [ ] Create `supabase/migrations/` directory
- [ ] Install PNPM via corepack
- [ ] Create root `package.json` for workspace
- [ ] Add `.cursor/rules.md` with project guidelines

## MCP Configuration

- [ ] Configure Nuxt UI MCP server
- [ ] Configure Supabase MCP server
- [ ] Configure AWS MCP server (Transcribe/Lambda)
- [ ] Test MCP connections in Cursor

## Frontend Setup

- [ ] Initialize Nuxt 3 project in `frontend/`
- [ ] Install `@nuxt/ui` module
- [ ] Install `tresjs` and `@tresjs/cientos`
- [ ] Install `@supabase/nuxt` module
- [ ] Install TailwindCSS and configure
- [ ] Set up `frontend/nuxt.config.ts` with modules
- [ ] Create `frontend/assets/css/tailwind.css`
- [ ] Configure `tailwind.config.js` with content paths
- [ ] Set up PWA support (Nuxt auto-generates manifest)

## Backend Setup

- [ ] Initialize FastAPI project in `backend/`
- [ ] Create `backend/main.py` entry point
- [ ] Set up `backend/requirements.txt` with dependencies:
  - [ ] fastapi
  - [ ] uvicorn
  - [ ] spacy
  - [ ] nltk
  - [ ] scikit-learn
  - [ ] boto3
- [ ] Create `backend/nlp/` directory structure
- [ ] Set up virtual environment and install dependencies

## Supabase Infrastructure

- [ ] Create Supabase project
- [ ] Set up authentication (email/password)
- [ ] Design database schema:
  - [ ] Users table
  - [ ] Students table
  - [ ] Teachers table
  - [ ] Vocabulary words table
  - [ ] Relic resonance profiles table
  - [ ] SRS progress table (ease factor, interval, due date)
  - [ ] Session history table
  - [ ] Quest/raid data table
- [ ] Create initial migration files
- [ ] Set up Row Level Security (RLS) policies
- [ ] Configure Supabase Realtime for multiplayer sync
- [ ] Set up Supabase Edge Functions (if needed)

## Story Spark Profiling (P0)

- [ ] Create `frontend/pages/spark.vue` onboarding page
- [ ] Implement voice input capture (Web Speech API)
- [ ] Implement text input fallback
- [ ] Create `frontend/composables/useVocabInput.ts` for dual input modes
- [ ] Add voice/text toggle with Nuxt UI `<USwitch>`
- [ ] Set up AWS Transcribe fallback for noisy environments
- [ ] Create `backend/nlp/profiler.py`:
  - [ ] Transcribe voice/text input
  - [ ] Analyze via spaCy/NLTK
  - [ ] Score against COCA/Lexile corpora
  - [ ] Generate relic resonance profile
- [ ] Map words to "whisper relics" (basic) to "thunder relics" (advanced)
- [ ] Store profile in Supabase

## Relic Resonance Engine (P0)

- [ ] Create `backend/nlp/recommender.py`:
  - [ ] Calculate ZPD-balanced words (70-80% learnability)
  - [ ] Suggest 5-7 words per profile
  - [ ] Implement dynamic pacing logic (mastery → evolution)
- [ ] Create `frontend/composables/useProceduralRelic.ts`:
  - [ ] Generate 3D artifacts using TresJS
  - [ ] Integrate Cientos helpers for interactions
- [ ] Display relic resonance meters in UI
- [ ] Implement relic glow effects based on mastery

## Spaced Repetition System (P0)

- [ ] Create `backend/nlp/srs.py`:
  - [ ] Implement SM-2 algorithm (ease factor, interval, due date)
  - [ ] Calculate next review date
  - [ ] Update ease factor based on performance
- [ ] Create `frontend/composables/useSRS.ts`:
  - [ ] Fetch due words from backend
  - [ ] Track session progress
  - [ ] Submit activity results
- [ ] Create SRS database schema in Supabase
- [ ] Implement session flow:
  - [ ] "Start Session" button
  - [ ] Mix 4 new words + 6-8 reviews
  - [ ] 10-minute timer
  - [ ] Basic progress display ("3/5 mastered")

## Daily Session - 6 Core Activities (P0)

- [ ] Create `frontend/pages/session.vue` main session page
- [ ] Implement Activity 1: Flashcard Introduction
  - [ ] Display word + definition + example sentence
  - [ ] TTS reads word
  - [ ] Student repeats (voice capture)
- [ ] Implement Activity 2: Meaning Multiple Choice
  - [ ] 4 options, 1 correct
  - [ ] Voice prompt: "Tap the meaning of *word*"
- [ ] Implement Activity 3: Dictated Spelling
  - [ ] Hear word → type it
  - [ ] Voice prompt: "Spell *word*"
- [ ] Implement Activity 4: Context Fill-in-the-Blank
  - [ ] Sentence with gap
  - [ ] Voice prompt: "Complete: [sentence]"
- [ ] Implement Activity 5: Synonym/Antonym Selection
  - [ ] 4 options
  - [ ] Label as "same" or "opposite"
- [ ] Implement Activity 6: Sentence Generation
  - [ ] Prompt: "Use *word* in a sentence about your day"
  - [ ] AI scoring (grammar, relevance)
- [ ] Create activity routing/navigation
- [ ] Implement progress tracking per activity
- [ ] Add completion celebration (Nuxt UI `<UConfetti>`)

## Resilient Raid - 3D Quest Game (P0)

- [ ] Create `frontend/pages/games/raid.vue`
- [ ] Set up TresJS canvas with `<TresCanvas>`
- [ ] Integrate Cientos `<OrbitControls>` for relic inspection
- [ ] Create procedural relic meshes (TresJS IcosahedronGeometry)
- [ ] Load 3D models from poly.pizza (crystals, fortresses, orbs)
- [ ] Implement dynamic quest generation:
  - [ ] Personalized raids based on transcript themes
  - [ ] Map themes (e.g., soccer → teamwork → Resilient Raid)
- [ ] Implement full skill coverage:
  - [ ] Spelling challenges
  - [ ] Writing challenges
  - [ ] Speaking challenges
  - [ ] Reading challenges
  - [ ] Etymology challenges
- [ ] Add relic fusion mechanics (basic + advanced = hybrid)
- [ ] Create realm visualizations (soccer-themed bastions, etc.)
- [ ] Implement dynamic lighting based on mastery
- [ ] Add procedural turf/environment for context quests

## Dual Input Modes (P0)

- [ ] Complete Web Speech API integration
- [ ] Complete AWS Transcribe fallback
- [ ] Implement text input (typing, drag-and-drop, emoji)
- [ ] Add voice/text toggle UI component
- [ ] Handle input mode switching during activities

## Multiplayer Sync (P0)

- [ ] Set up Supabase Realtime subscriptions
- [ ] Implement 2-8 player room system
- [ ] Create shared relic fusion mechanics
- [ ] Sync player progress in real-time
- [ ] Add multiplayer UI indicators

## Progress Tracking & Legend Ledger (P0)

- [ ] Create progress database schema
- [ ] Implement streak counter
- [ ] Create "Legend Ledger" view
- [ ] Display mastery progress ("3/5 mastered")
- [ ] Add progress timeline (Nuxt UI `<UTimeline>`)
- [ ] Implement progress persistence

## Teacher Dashboard (P1)

- [ ] Create teacher dashboard page
- [ ] Implement session deployment UI
- [ ] Create resonance meters visualization
- [ ] Add export reports (CSV/PDF)
- [ ] Implement "who's mastering what" visual dashboard
- [ ] Create parent share link system (`palab.am/student/abc?share=parent`)

## Progress Export (P1)

- [ ] Implement one-click lesson plans export
- [ ] Add IEP notes export
- [ ] Create parent summaries export
- [ ] Format exports for teacher use

## Procedural 3D Relics (P2)

- [ ] Enhance `useProceduralRelic.ts`:
  - [ ] Generate icosahedrons morphing by word length
  - [ ] Add geometry generation logic
  - [ ] Implement morph animations

## Voice Feedback via AWS Transcribe (P2)

- [ ] Integrate pronunciation scoring
- [ ] Add prosody boosts
- [ ] Implement voice quality analysis
- [ ] Provide feedback to students

## Parent Portal (P2)

- [ ] Create parent login system
- [ ] Build progress history view
- [ ] Add share link functionality
- [ ] Implement parent dashboard

## Accessibility & UI Polish

- [ ] Implement WCAG 2.1 AA compliance
- [ ] Add voice fallback for all interactions
- [ ] Create high contrast mode
- [ ] Add screen reader support
- [ ] Implement age-appropriate UI:
  - [ ] Toddler mode: Plush animals, big buttons, voice-only
  - [ ] Middle school mode: 3D realms, multiplayer
  - [ ] Adult mode: Clean, dark mode, advanced themes
- [ ] Add colorblind-safe palettes
- [ ] Ensure large tap targets for toddlers

## Performance Optimization

- [ ] Optimize session load time (<3s target)
- [ ] Ensure 3D models <10k triangles
- [ ] Implement lazy loading for 3D assets
- [ ] Optimize parallel processing of 100+ transcripts (<5 min)
- [ ] Add performance monitoring

## Security & Compliance

- [ ] Ensure FERPA compliance
- [ ] Anonymize voice transcripts
- [ ] Review and test all RLS policies
- [ ] Implement secure authentication flows
- [ ] Add input validation and error handling

## Testing & Deployment

- [ ] Set up testing framework
- [ ] Write unit tests for SRS algorithm
- [ ] Write integration tests for API endpoints
- [ ] Test multiplayer sync functionality
- [ ] Test voice input across browsers
- [ ] Set up Vercel deployment for frontend
- [ ] Set up AWS Lambda deployment for backend
- [ ] Configure environment variables
- [ ] Set up CI/CD pipeline

## Documentation

- [ ] Create API documentation
- [ ] Document SRS algorithm implementation
- [ ] Create developer setup guide
- [ ] Document MCP configuration
- [ ] Add inline code comments
- [ ] Create user guides (teacher, student, parent)

