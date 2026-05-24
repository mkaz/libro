# Contributing to Libro

Libro is a hobby project, but contributions are welcome.

## Getting Started

1. Fork and clone the repo
2. Install dependencies: `npm install`
3. Run the dev build: `just dev`

## Development

`just dev` builds the Electron main process, starts the Vite dev server, then launches the app. Vite handles hot-reload for renderer changes. If you change anything in `electron/`, restart `just dev`.

## Making Changes

Follow the pattern in CLAUDE.md for adding new features — types in `shared/types.ts`, queries in `electron/db/`, IPC handler in `electron/ipc.ts`, wired up in `preload.ts` and `src/lib/api.ts`, then the React component in `src/features/`.

Run `npm run typecheck` and `npm run lint` before submitting.

## Submitting Changes

Open a pull request with a plain description of what you changed and why. No fancy templates needed.
