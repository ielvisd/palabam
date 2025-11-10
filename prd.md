# Palabam: Personalized Vocabulary Recommendation Engine for Middle School Students

**Organization:** Flourish Schools  
**Project ID:** JnGyV0Xlx2AEiL31nu7J_1761523676397  
**Version:** 2.0 (Aligned with Original Spec)  
**Date:** November 10, 2025

---

## 1. Executive Summary

Palabam is an AI-powered vocabulary recommendation engine that automates the identification of vocabulary gaps in middle school students' language use. By analyzing student conversation transcripts and writing samples, the system provides educators with personalized vocabulary word recommendations tailored to each student's proficiency level. This solution significantly reduces teacher workload while accelerating student vocabulary acquisition through data-driven insights.

- **Automated Gap Detection**: AI analyzes transcripts using NLP (spaCy/NLTK) and compares against COCA/Lexile corpora
- **Personalized Recommendations**: Suggests 5-7 ZPD-balanced words per student (70-80% learnability)
- **Educator-Focused Dashboard**: Clear visualization of recommendations per student with export capabilities
- **Cloud-Based Architecture**: FastAPI backend, Nuxt 3 frontend, Supabase database

---

## 2. Problem Statement

Middle school educators currently struggle with manually identifying vocabulary gaps in students' language use. This process is time-consuming and often fails to provide personalized recommendations that align with each student's current proficiency level. The lack of tailored vocabulary development opportunities may hinder students' language acquisition and overall academic performance. An automated system that can analyze language use and provide strategic vocabulary expansion opportunities is needed to address this gap.

---

## 3. Goals & Success Metrics

| Goal | Success Metric |
|------|----------------|
| Automate gap detection | 15–25% increase in novel word usage over 4 weeks |
| Provide personalized recommendations | 80%+ of recommendations rated "useful" by educators |
| Reduce teacher workload | 50% reduction in manual analysis time (survey) |

---

## 4. Target Users & Personas

**Primary Users: Middle School Educators**

- **Persona: Ms. Rivera, 7th-Grade ELA Teacher**
  - Manages 120 students across 5 classes; tech-savvy but time-strapped.
  - Needs: Efficient tools to analyze and recommend vocabulary; desire to enhance student skills without manual effort.

**Secondary Users: Middle School Students**

- **Persona: Alex, 12-Year-Old 6th Grader**
  - Enjoys gamified apps; uses school iPad daily.
  - Needs: Personalized, challenging yet achievable vocabulary; support in improving language skills.

---

## 5. User Stories

- As a middle school educator, I want to receive a list of vocabulary words tailored to each student's proficiency level so that I can efficiently enhance their language skills.
- As a middle school educator, I want to upload or paste student transcripts and writing samples so that the system can analyze them automatically.
- As a middle school educator, I want to view all recommended words for my students in a dashboard so that I can plan vocabulary instruction efficiently.
- As a middle school educator, I want to export recommendations as CSV or PDF so that I can share them with parents or include them in lesson plans.
- As a middle school student, I want to be challenged with new vocabulary words that I can realistically learn and use effectively, so that I can improve my language proficiency.

---

## 6. Functional Requirements

### P0: Must-have

- **Transcript/Writing Sample Input**
  - System accepts student conversation transcripts and writing samples via upload or paste
  - Supports both text input and voice transcription (Web Speech API + AWS Transcribe fallback)
  - Validates input quality (minimum length, format checks)

- **Story Spark Profiling**
  - Voice/text input → transcribed → analyzed via spaCy/NLTK
  - Scored against COCA/Lexile corpora
  - Generates vocabulary profile with word difficulty scores
  - No grade labels; words abstracted as "whisper relics" (basic) to "thunder relics" (advanced)

- **Gap Identification**
  - AI identifies vocabulary gaps by comparing student usage against corpora
  - Calculates current vocabulary level
  - Identifies areas for growth

- **Word Recommendation Engine**
  - Suggests 5–7 ZPD-balanced words (70–80% learnability) per student
  - Filters out words already in student's vocabulary
  - Maintains dynamic list of recommended words

- **Educator Dashboard**
  - View all students with their recommended words
  - Filter/search by student name or word
  - View transcript history per student
  - Export recommendations (CSV/PDF)
  - Progress tracking (which words recommended when)

### P1: Should-have

- **Batch Processing**
  - Process multiple students' transcripts simultaneously
  - Bulk upload of transcripts/writing samples

- **Integration with Educational Platforms**
  - Google Classroom integration (fallback to manual input)
  - Import student data from SIS systems

- **Customizable Recommendation Settings**
  - Adjust ZPD range per student
  - Set recommendation count preferences
  - Filter by word type or theme

### P2: Nice-to-have

- **Gamified Vocabulary Challenges**
  - Student-facing activities for practicing recommended words
  - Progress tracking for student engagement

- **Advanced Analytics**
  - Vocabulary growth trends over time
  - Class-level vocabulary insights
  - Comparative analysis across students

---

## 7. Non-Functional Requirements

- **Performance**:
  - Parallel processing of 100+ transcripts in <5 min
  - Dashboard load time <2s
  - API response time <500ms for recommendations

- **Scalability**:
  - Handle 1,000+ concurrent users
  - Auto-scale on Vercel + AWS
  - Support for large batch processing

- **Security**:
  - FERPA-compliant
  - Anonymized voice transcripts
  - Supabase Row Level Security (RLS)
  - Secure file upload handling

- **Reliability**:
  - 99% uptime
  - Error handling for malformed inputs
  - Graceful degradation for API failures

- **Accessibility**:
  - WCAG 2.1 AA compliance
  - Screen reader support
  - Keyboard navigation

---

## 8. User Experience & Design Considerations

- **Workflows**:
  1. **Upload Transcript/Writing Sample** → 2. **Analysis & Gap Detection** → 3. **View Recommendations** → 4. **Export & Use**

- **Interface Principles**:
  - Clear visualization: Student list, recommended words, progress indicators
  - Nuxt UI components: `<UCard>`, `<UButton>`, `<UProgress>`, `<UTable>`
  - Simple, educator-focused design
  - Mobile-responsive layout

- **Accessibility Needs**:
  - High contrast, readable fonts
  - Large click targets
  - Clear error messages
  - Loading states for async operations

---

## 9. Technical Requirements

### System Architecture

- **Cloud-based deployment**
  - **Frontend**: Vercel (Nuxt 3)
  - **Backend**: FastAPI (AWS Lambda or direct deployment)
  - **Database/Auth**: Supabase
  - **Voice Fallback**: AWS Transcribe (optional)

### Monorepo Structure

```
palabam/
├── backend/                  # FastAPI
│   ├── main.py
│   ├── nlp/
│   │   ├── profiler.py       # Transcript analysis
│   │   ├── recommender.py    # Word recommendations
│   │   └── dataset_loader.py # COCA/Lexile data
│   ├── db/
│   │   ├── profiles.py       # Student profiles
│   │   ├── words.py          # Vocabulary database
│   │   └── supabase_client.py
│   └── requirements.txt
├── frontend/                 # Nuxt 3
│   ├── app.vue
│   ├── pages/
│   │   ├── index.vue         # Educator landing page
│   │   ├── spark.vue         # Transcript input
│   │   └── dashboard.vue     # Educator dashboard
│   ├── composables/
│   │   └── useVocabInput.ts  # Transcript input handling
│   ├── assets/css/tailwind.css
│   └── nuxt.config.ts
├── supabase/
│   └── migrations/
└── pnpm-workspace.yaml
```

### Package Manager

- **PNPM** — Required for monorepo
  - Faster, disk-efficient, strict dependency hoisting
  - Cursor auto-detects `pnpm-lock.yaml`

#### Frontend Dependencies (`frontend/package.json`)

```bash
pnpm add @nuxt/ui @supabase/nuxt
pnpm add -D tailwindcss
```

#### Backend Dependencies (`backend/requirements.txt`)

```txt
fastapi
uvicorn
spacy
nltk
scikit-learn
boto3
supabase
```

---

## 10. Dependencies & Assumptions

- Availability of student conversation transcripts and writing samples for analysis
- Integration capabilities with existing school data management systems (Google Classroom)
- Access to Vercel, Supabase, AWS (free tier for dev)
- COCA and Lexile datasets available for vocabulary scoring

---

## 11. Out of Scope

- Direct classroom implementation or training for educators
- Development of proprietary AI frameworks beyond publicly available tools
- Real-time speech-to-text conversion (assumes text data is pre-processed or uses Web Speech API)
- Student-facing learning platform (gamification, activities, SRS)
- Mobile app (web app is mobile-responsive)
- Parent portal login (export functionality covers sharing needs)

---

## 12. Pedagogical Foundation

All recommendations incorporate evidence-based practices:

| Practice | Implementation in Palabam |
|----------|---------------------------|
| Explicit Word Selection | 5-7 high-utility words per student; student-friendly definitions + examples |
| Zone of Proximal Development (ZPD) | Words at 70-80% learnability (slightly above current level) |
| Vocabulary Gap Analysis | Compare student usage against age-appropriate corpora (COCA/Lexile) |
| Personalized Recommendations | Tailored to each student's current vocabulary profile |

**Alignment**: National Reading Panel, Beck et al. (2002), WWC (2011), Hirsch (2006)

---

## 13. Database Schema

### Core Tables

- **profiles**: Student vocabulary profiles with resonance data and word scores
- **words**: Vocabulary database with difficulty scores, definitions, examples
- **recommendations**: Track recommended words per student with timestamps
- **students**: Student information linked to users
- **teachers**: Teacher information linked to users

### Tables Removed/Deferred

- **srs_progress**: Spaced repetition data (moved to future enhancements)
- **sessions**: Student learning sessions (moved to future enhancements)
- **quests**: 3D game quests (moved to future enhancements)

---

## 14. API Endpoints

### Profile Endpoints

- `POST /api/profile/` - Create profile from transcript
  - Request: `{ transcript: string, inputMode: string, student_id?: string }`
  - Response: `{ profile_id, word_scores, resonance_data, vocabulary_level, recommended_words }`

### Recommendation Endpoints

- `POST /api/recommend/` - Get word recommendations
  - Request: `{ profile: object, count: number, zpd_range: tuple }`
  - Response: `{ recommended_words: array }`

---

## 15. Future Enhancements

The following features were part of the original vision but are deferred to focus on the core recommendation engine:

- **Spaced Repetition System (SRS)**: SM-2 algorithm for long-term retention
- **Student Learning Activities**: Flashcards, multiple choice, spelling, fill-in-the-blank, synonym, sentence generation
- **3D Gamification**: TresJS-based 3D relics and multiplayer raids
- **Real-time Multiplayer**: Supabase Realtime for collaborative learning
- **Advanced Voice Features**: Pronunciation scoring, prosody analysis

These features may be added in future versions based on educator feedback and usage patterns.
