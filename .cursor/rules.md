# Palabam Project Rules

## Package Manager
- **NEVER use npm** - Always use `pnpm` for all package management
- Use `pnpm install`, `pnpm add`, `pnpm exec`, etc.
- The project uses PNPM workspaces for monorepo structure

## MCP Integration
- Use Nuxt UI MCP for component documentation and examples
- Use Supabase MCP for database operations, migrations, and realtime
- Use AWS MCP for Transcribe and Lambda operations
- Reference MCP documentation when implementing features

## 3D Assets
- All 3D models from poly.pizza (CC-BY low-poly GLTF)
- Use TresJS primitives for procedural relics
- Use Cientos helpers for interactions (OrbitControls, effects)
- Keep models under 10k triangles for performance

## No Grade Labels
- Use "relic resonance" system instead of grade levels
- Words scale from "whisper relics" (basic) to "thunder relics" (advanced)
- Same engine works for toddlers to adults

## SRS Implementation
- Implement 10-minute SRS sessions with 6 core activities
- Use SM-2 algorithm (ease factor, interval, due date)
- Mix 4 new words + 6-8 reviews per session

## Code Style
- Frontend: Vue 3 Composition API with TypeScript
- Backend: FastAPI with async/await patterns
- Use Nuxt UI components for consistent UI
- Follow Nuxt 3 conventions (auto-imports, composables)

## References
- TresJS cookbook for animations and patterns
- Cientos for clickable relics and interactions
- Aviator game repo for game loop patterns
- Agorespace for immersive realm visualizations

