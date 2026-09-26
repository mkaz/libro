# Libro Desktop

Libro is an Electron reading tracker with a local SQLite database. Books, reviews, reading lists, and downloaded covers live on your computer.

## Covers

When adding a book or choosing a cover for an existing book, Libro searches Open Library first. If Open Library returns covers you don't want, select **Search Google Books for more covers** to add Google Books options. If Open Library finds none, Libro searches Google Books automatically. Select a cover to save it locally.

A Google Books API key is **optional**. It gives you extra cover art choices when Open Library's results aren't suitable. Without a key, Open Library cover search still works, but Google Books may reject requests (HTTP 429).

To use Google Books, you need a Google Cloud project with the **Books API enabled**; a key alone is not enough.

1. In the [Google Cloud Console](https://console.cloud.google.com/apis/credentials), select or create a project, then enable **Books API** in that project.
2. Follow [Google's API key instructions](https://developers.google.com/books/docs/v1/using#APIKey): select **Create credentials > API key**. If you restrict the key to specific APIs, allow **Books API**. Public book searches do not require OAuth 2.0.
3. In Libro, enter the key under **Settings > Google Books API key** and select **Save key**.

Libro uses the key immediately and stores it in `settings.json` in the current data directory (not encrypted). Switching data directories switches keys; **Remove key** deletes the saved key.

Alternatively, set `GOOGLE_BOOKS_API_KEY` in Libro's environment and restart the app. A key entered in Settings takes precedence. For example, when running from a terminal:

```bash
GOOGLE_BOOKS_API_KEY=your-key npm run dev
```

Keep the key private; don't commit `settings.json` containing a key to the repository.

## Development

Install Node.js 22.12 or newer and npm, then install dependencies and start the app:

```bash
npm ci
npm run dev
```

`npm ci` removes the existing `node_modules` directory and installs the versions in `package-lock.json`. It does not update the lockfile. This project also runs `electron-builder install-app-deps` after installation to rebuild `better-sqlite3` for Electron; loading it directly with Node.js may then fail with a `NODE_MODULE_VERSION` mismatch. The remaining deprecation warnings come from `electron-builder` dependencies and do not mean the install failed; check the command's exit status and any `npm error` lines. The `esbuild` override in `package.json` pins a patched version while `tsup` still requests an older range.

Check changes with `npm run lint` and `npm run build`.

To use an isolated data directory for development, pass it with `--data-dir`:

```bash
npm run dev -- --data-dir ./data/cover-test
```

Libro creates this layout as files are needed:

```text
cover-test/
├── libro.db
├── covers/
└── settings.json
```

The older `--db <database-path>` option remains available for testing a specific database file. Covers are stored in a `covers` directory beside that file.

## Data directory

A packaged app stores data in Electron's per-user application directory by default. On macOS this is normally `~/Library/Application Support/Libro Desktop`. Use **Settings > Choose directory…** to select a directory containing `libro.db`, `covers/`, and `settings.json`. Libro remembers the selection in `libro-config.json` under the per-user application directory. Selecting a directory switches to the data already there (or creates a new database); it does not move data from the previous directory. The default list/grid results view and any saved Google Books API key are stored in `settings.json` inside the active data directory.

The database path is resolved in this order:

1. `LIBRO_DATA_DIR_OVERRIDE` or the legacy `LIBRO_DB_OVERRIDE`
2. An existing `libro.db` in the current working directory
3. `LIBRO_DATA_DIR` or the legacy `LIBRO_DB`
4. The directory saved through **Settings > Choose directory…**
5. Electron's per-user application directory

`LIBRO_DATA_DIR` and `LIBRO_DATA_DIR_OVERRIDE` name directories. Libro uses `libro.db` and `covers/` inside them. The `LIBRO_DB` variables name a database file directly and are retained for compatibility. Directory selection is disabled while an environment variable or a `libro.db` in the working directory takes precedence.
