import { defineConfig } from 'tsup'

export default defineConfig({
  entry: ['electron/main.ts', 'electron/preload.ts'],
  outDir: 'dist-electron',
  platform: 'node',
  format: ['cjs'],
  target: 'node20',
  bundle: true,
  splitting: false,
  sourcemap: true,
  clean: true,
  external: ['electron'],
  outExtension() {
    return {
      js: '.cjs',
    }
  },
})
