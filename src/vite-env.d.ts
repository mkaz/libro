/// <reference types="vite/client" />

import type { LibroApi } from '../shared/types'

declare global {
  interface Window {
    libro?: LibroApi
  }
}
