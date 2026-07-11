# CLAUDE.md

This file provides guidance to LLMs working with code in this repository.

## Project Overview

Libro is a desktop reading tracker built with Electron + React + Vite. It uses a local SQLite database.

## Development Commands

```bash
npm run dev        # Start Vite renderer + Electron (hot-reload)
npm run build      # Typecheck, build renderer, build Electron main/preload
npm run package    # Full build + electron-builder → .dmg
npm run typecheck  # tsc on both renderer and Electron tsconfigs
npm run lint       # eslint
```

## Code Architecture

### Project Structure

```
libro/
├── electron/
│   ├── main.ts       # Electron main process, BrowserWindow setup
│   ├── preload.ts    # Context bridge — exposes LibroApi to renderer
│   ├── ipc.ts        # IPC handler registration
│   └── db/
│       ├── client.ts # Database singleton, path resolution, migration call
│       ├── migrate.ts # Schema migrations
│       ├── books.ts  # Book/review queries
│       ├── reports.ts # Year counts, author counts, review filters
│       └── lists.ts  # Reading list CRUD
├── shared/
│   └── types.ts      # Shared TypeScript interfaces (LibroApi, all input/output types)
└── src/              # React renderer
    ├── App.tsx        # Shell with nav (Books, Reports, Search, Lists, Add Book)
    ├── lib/
    │   ├── api.ts     # Typed wrapper around window.libro (the context bridge)
    │   ├── ratings.ts # Star rating helpers
    │   └── ReviewTable.tsx # Shared review table component
    └── features/
        ├── books/BooksByYearView.tsx
        ├── reports/ReportsView.tsx
        ├── search/SearchView.tsx
        ├── lists/ListsView.tsx
        └── add/AddBookReviewForm.tsx
```

### Key Technologies

- **Framework**: Electron 33 + React 19 + Vite 5
- **Database**: better-sqlite3 (synchronous, runs in main process only)
- **Styling**: Halfmoon CSS
- **Build**: tsup for Electron main/preload, Vite for renderer
- **Packaging**: electron-builder (targets macOS DMG)
- **Package Manager**: npm

## Data Model

### Books vs Reviews

The application separates **books** from **reviews** to support:
- Books without reviews (unread books on a reading list)
- Multiple reviews per book (re-reads)

**Tables:**
1. `books` - Book metadata (title, author, pub_year, pages, genre)
2. `reviews` - Reading records (book_id, date_read, rating, review)
3. `reading_lists` - Curated book collections
4. `reading_list_books` - Many-to-many join table (with priority and added_date)

**Database Schema:**

```sql
CREATE TABLE books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    pub_year INTEGER,
    pages INTEGER,
    genre TEXT
);

CREATE TABLE reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id INTEGER,
    date_read DATE,
    rating INTEGER,
    review TEXT,
    FOREIGN KEY(book_id) REFERENCES books(id)
);

CREATE TABLE reading_lists (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    created_date DATE DEFAULT CURRENT_DATE
);

CREATE TABLE reading_list_books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    list_id INTEGER NOT NULL,
    book_id INTEGER NOT NULL,
    added_date DATE DEFAULT CURRENT_DATE,
    priority INTEGER DEFAULT 0,
    FOREIGN KEY(list_id) REFERENCES reading_lists(id) ON DELETE CASCADE,
    FOREIGN KEY(book_id) REFERENCES books(id) ON DELETE CASCADE,
    UNIQUE(list_id, book_id)
);
```

## IPC Architecture

All database access happens in the main process. The renderer never touches the database directly.

- `preload.ts` exposes a typed `LibroApi` object on `window.libro` via `contextBridge`
- `src/lib/api.ts` re-exports this as `api` for use in React components
- `ipc.ts` registers `ipcMain.handle` handlers that call into `electron/db/` functions

IPC channel naming: `namespace:verb-noun` (e.g. `books:add-book-review`, `lists:get-by-id`).

## Database Location

Priority order:

1. `libro.db` in cwd (if it exists)
2. `LIBRO_DB` environment variable
3. `{appData}/Libro/mkaz/libro.db`

## Adding a New Feature

1. Add types to `shared/types.ts` (input, output, and the `LibroApi` interface entry)
2. Add the query function in the appropriate `electron/db/*.ts` file
3. Register an IPC handler in `electron/ipc.ts`
4. Wire it up in `preload.ts` and `src/lib/api.ts`
5. Build the React component in `src/features/`

## Code Style

- Strict TypeScript; all types defined in `shared/types.ts`
- Two separate tsconfig targets: `tsconfig.app.json` (renderer) and `tsconfig.electron.json` (main/preload)
- No ORM; raw SQL via better-sqlite3 synchronous API
- eslint with react-hooks and react-refresh plugins
