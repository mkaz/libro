# Libro Desktop

## Development

Start Libro with its configured data directory:

```bash
npm run dev
```

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

## Vite template notes

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Oxc](https://oxc.rs)
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/)

## React Compiler

The React Compiler is not enabled on this template because of its impact on dev & build performances. To add it, see [this documentation](https://react.dev/learn/react-compiler/installation).

## Expanding the ESLint configuration

If you are developing a production application, we recommend updating the configuration to enable type-aware lint rules:

```js
export default defineConfig([
  globalIgnores(['dist']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      // Other configs...

      // Remove tseslint.configs.recommended and replace with this
      tseslint.configs.recommendedTypeChecked,
      // Alternatively, use this for stricter rules
      tseslint.configs.strictTypeChecked,
      // Optionally, add this for stylistic rules
      tseslint.configs.stylisticTypeChecked,

      // Other configs...
    ],
    languageOptions: {
      parserOptions: {
        project: ['./tsconfig.node.json', './tsconfig.app.json'],
        tsconfigRootDir: import.meta.dirname,
      },
      // other options...
    },
  },
])
```

You can also install [eslint-plugin-react-x](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-x) and [eslint-plugin-react-dom](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-dom) for React-specific lint rules:

```js
// eslint.config.js
import reactX from 'eslint-plugin-react-x'
import reactDom from 'eslint-plugin-react-dom'

export default defineConfig([
  globalIgnores(['dist']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      // Other configs...
      // Enable lint rules for React
      reactX.configs['recommended-typescript'],
      // Enable lint rules for React DOM
      reactDom.configs.recommended,
    ],
    languageOptions: {
      parserOptions: {
        project: ['./tsconfig.node.json', './tsconfig.app.json'],
        tsconfigRootDir: import.meta.dirname,
      },
      // other options...
    },
  },
])
```
