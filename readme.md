# Libro Desktop

Libro is an Electron reading tracker with a local SQLite database. Books, reviews, reading lists, and downloaded covers live on your computer.

## Development

Install Node.js and npm, then install dependencies and start the app:

```bash
npm ci
npm run dev
```

`npm ci` removes the existing `node_modules` directory and installs the versions in `package-lock.json`. It does not update the lockfile. This project also runs `electron-builder install-app-deps` after installation to rebuild `better-sqlite3` for Electron; loading it directly with Node.js may then fail with a `NODE_MODULE_VERSION` mismatch. Some deprecation warnings come from transitive dependencies and do not mean the install failed; check the command's exit status and any `npm error` lines.

Check changes with `npm run lint` and `npm run build`.

To use an isolated data directory for development, pass it with `--data-dir`:

```bash
npm run dev -- --data-dir ./data/cover-test
```

Libro creates this layout as files are needed:

```text
cover-test/
├── libro.db
└── covers/
```

The older `--db <database-path>` option remains available for testing a specific database file. Covers are stored in a `covers` directory beside that file.

## Data directory

A packaged app stores data in Electron's per-user application directory by default. On macOS this is normally `~/Library/Application Support/Libro Desktop`. Use **File > Open Database…** to select another database; Libro remembers its containing directory in `libro-config.json` under the per-user application directory.

The database path is resolved in this order:

1. `LIBRO_DATA_DIR_OVERRIDE` or the legacy `LIBRO_DB_OVERRIDE`
2. An existing `libro.db` in the current working directory
3. `LIBRO_DATA_DIR` or the legacy `LIBRO_DB`
4. The directory saved through **File > Open Database…**
5. Electron's per-user application directory

`LIBRO_DATA_DIR` and `LIBRO_DATA_DIR_OVERRIDE` name directories. Libro uses `libro.db` and `covers/` inside them. The `LIBRO_DB` variables name a database file directly and are retained for compatibility.
