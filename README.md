# Palabam

AI-Powered Vocabulary Odyssey for Middle School Mastery

## Overview

Palabam is an explosive AI game that turns middle school vocabulary gaps into multiplayer 3D raids, powered by a scientifically proven spaced repetition engine and advanced TresJS with Cientos. Students complete 10-minute daily sessions that blend new word introduction with timed reviews of past relics, ensuring long-term retention.

## Tech Stack

- **Frontend**: Nuxt 3 + Vue 3 + TresJS + Cientos
- **Backend**: FastAPI (Python)
- **Database**: Supabase (PostgreSQL)
- **3D Engine**: TresJS (Three.js wrapper)
- **Package Manager**: PNPM (monorepo)

## Project Structure

```
palabam/
├── frontend/          # Nuxt 3 application
├── backend/           # FastAPI server
├── supabase/          # Database migrations
└── pnpm-workspace.yaml
```

## Getting Started

### Prerequisites

- Node.js 18+
- PNPM 8+
- Python 3.9+
- Supabase project (existing)
- AWS credentials (for Transcribe)

### Installation

1. **Install PNPM** (if not already installed):
```bash
corepack enable
corepack prepare pnpm@latest --activate
```

2. **Install dependencies**:
```bash
pnpm install
```

3. **Backend Setup**:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
```

4. **Environment Variables**:

Create `.env` files in both `frontend/` and `backend/`:

**frontend/.env**:
```
NUXT_PUBLIC_SUPABASE_URL=your_supabase_url
NUXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
NUXT_PUBLIC_API_URL=http://localhost:8000
```

**backend/.env**:
```
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_service_key
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
AWS_REGION=us-east-1
```

5. **Database Setup**:

Apply migrations to your Supabase project:
```bash
# Using Supabase CLI or dashboard
supabase db push
# Or manually run migrations from supabase/migrations/
```

6. **Generate Datasets** (or use existing ones):

The project includes a script to generate word frequency and difficulty datasets:

```bash
cd backend
pip install wordfreq  # Optional: for better frequency data
python3 scripts/generate_datasets.py
```

This creates:
- `backend/data/coca_frequency.json` - Word frequency data
- `backend/data/lexile_scores.json` - Word difficulty scores

**Note**: The script works without `wordfreq` (uses estimates), but installing `wordfreq` provides more accurate data. You can also replace these with official COCA/Lexile datasets later.

See `backend/data/README.md` for details on using official datasets.

### Running the Application

**Frontend**:
```bash
pnpm dev:frontend
# Or
cd frontend && pnpm dev
```

**Backend**:
```bash
pnpm dev:backend
# Or
cd backend && pnpm dev
```

## Features Implemented

### P0 (Must-have) Features

✅ **Story Spark Profiling**
- Voice/text input with Web Speech API
- AWS Transcribe fallback
- NLP analysis with spaCy/NLTK
- COCA/Lexile word difficulty scoring
- Relic resonance profile generation

✅ **Relic Resonance Engine**
- ZPD-balanced word recommendations (70-80% learnability)
- Dynamic pacing logic
- 3D procedural relic generation with TresJS

✅ **Spaced Repetition System (SRS)**
- SM-2 algorithm implementation
- 10-minute daily sessions
- Mix of 4 new words + 6-8 reviews

✅ **6 Core Activities**
- Flashcard Introduction
- Meaning Multiple Choice
- Dictated Spelling
- Context Fill-in-the-Blank
- Synonym/Antonym Selection
- Sentence Generation

✅ **3D Quest Raids**
- TresJS canvas with procedural relics
- Dynamic quest generation
- Relic fusion mechanics

✅ **Multiplayer Sync**
- Supabase Realtime subscriptions
- 2-8 player rooms
- Shared relic fusion

✅ **Progress Tracking**
- Legend Ledger view
- Streak counter
- Mastery progress visualization
- Timeline of achievements

## Development

### Code Style

- Frontend: Vue 3 Composition API with TypeScript
- Backend: FastAPI with async/await patterns
- Use Nuxt UI components for consistent UI
- Follow Nuxt 3 conventions (auto-imports, composables)

### Key Files

- `.cursor/rules.md` - Project guidelines and rules
- `architecture.md` - System architecture
- `prd.md` - Product requirements document
- `tasks.md` - Project task list

## Next Steps

1. **Dataset Integration**: Add COCA/Lexile datasets to `backend/data/`
2. **Database Integration**: Connect backend to Supabase for data persistence
3. **Authentication**: Implement Supabase Auth flows
4. **Testing**: Add unit and integration tests
5. **Deployment**: Set up Vercel (frontend) and AWS Lambda (backend)

## License

[Your License Here]
