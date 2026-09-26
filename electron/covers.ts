import { randomUUID } from 'node:crypto'
import { mkdir, rm, writeFile } from 'node:fs/promises'
import path from 'node:path'

import type {
  BookCoverCandidate,
  BookCoverSelection,
  BookCoverSource,
} from '../shared/types'
import { getCoversDirectory, getDataDirectory, getGoogleBooksApiKey } from './db/client'
import type { SavedBookCover } from './db/books'

const OPEN_LIBRARY_BASE_URL = 'https://openlibrary.org'
const OPEN_LIBRARY_COVERS_URL = 'https://covers.openlibrary.org'
const GOOGLE_BOOKS_API_URL = 'https://www.googleapis.com/books/v1/volumes'
const MAX_CANDIDATES = 12
const MAX_COVER_BYTES = 10 * 1024 * 1024
const REQUEST_TIMEOUT_MS = 15_000

interface OpenLibrarySearchDocument {
  key?: string
  title?: string
  author_name?: string[]
  first_publish_year?: number
  cover_i?: number
}

interface OpenLibraryEdition {
  key?: string
  title?: string
  publish_date?: string
  covers?: number[]
}

interface GoogleVolume {
  id?: string
  volumeInfo?: {
    title?: string
    authors?: string[]
    publishedDate?: string
    infoLink?: string
    imageLinks?: Record<string, string | undefined>
  }
}

class CoverServiceError extends Error {
  constructor(readonly status: number) {
    super(`Cover service returned ${status}.`)
  }
}

function requestHeaders(): HeadersInit {
  return {
    Accept: 'application/json',
    'User-Agent': 'Libro Desktop/0.2.2 (personal desktop reading tracker)',
  }
}

async function fetchJson<T>(url: URL): Promise<T> {
  const response = await fetch(url, {
    headers: requestHeaders(),
    signal: AbortSignal.timeout(REQUEST_TIMEOUT_MS),
  })

  if (!response.ok) {
    throw new CoverServiceError(response.status)
  }

  return response.json() as Promise<T>
}

function coverUrl(coverId: number, size: 'M' | 'L'): string {
  return `${OPEN_LIBRARY_COVERS_URL}/b/id/${coverId}-${size}.jpg?default=false`
}

function publicationYear(value: string | number | undefined): string | null {
  if (value === undefined) return null
  const match = String(value).match(/\b\d{4}\b/)
  return match?.[0] ?? null
}

async function findOpenLibraryCovers(
  title: string,
  author: string,
): Promise<BookCoverCandidate[]> {
  const searchUrl = new URL('/search.json', OPEN_LIBRARY_BASE_URL)
  searchUrl.searchParams.set('title', title)
  searchUrl.searchParams.set('author', author)
  searchUrl.searchParams.set('fields', 'key,title,author_name,first_publish_year,cover_i')
  searchUrl.searchParams.set('limit', '5')

  const search = await fetchJson<{ docs?: OpenLibrarySearchDocument[] }>(searchUrl)
  const work = search.docs?.find((document) => document.key?.startsWith('/works/'))
  if (!work?.key) return []
  const workKey = work.key

  // Open Library's default unidentified-client limit is one request per second.
  await new Promise((resolve) => setTimeout(resolve, 1_050))

  const editionsUrl = new URL(`${workKey}/editions.json`, OPEN_LIBRARY_BASE_URL)
  editionsUrl.searchParams.set('limit', '100')
  const editions = await fetchJson<{ entries?: OpenLibraryEdition[] }>(editionsUrl)
  const candidates: BookCoverCandidate[] = []
  const seenCoverIds = new Set<number>()

  function addCandidate(
    coverId: number,
    candidateTitle: string,
    year: string | null,
    sourceUrl: string,
  ): void {
    if (!Number.isInteger(coverId) || coverId <= 0 || seenCoverIds.has(coverId)) return
    seenCoverIds.add(coverId)
    candidates.push({
      source: 'openlibrary',
      sourceId: String(coverId),
      thumbnailUrl: coverUrl(coverId, 'M'),
      imageUrl: coverUrl(coverId, 'L'),
      title: candidateTitle,
      author: work?.author_name?.join(', ') || author,
      publicationYear: year,
      sourceUrl: new URL(sourceUrl, OPEN_LIBRARY_BASE_URL).toString(),
    })
  }

  for (const edition of editions.entries ?? []) {
    for (const coverId of edition.covers ?? []) {
      addCandidate(
        coverId,
        edition.title || work.title || title,
        publicationYear(edition.publish_date),
        edition.key || workKey,
      )
      if (candidates.length >= MAX_CANDIDATES) return candidates
    }
  }

  if (work.cover_i) {
    addCandidate(
      work.cover_i,
      work.title || title,
      publicationYear(work.first_publish_year),
      workKey,
    )
  }

  return candidates
}

function httpsUrl(value: string): string {
  return value.replace(/^http:\/\//, 'https://')
}

async function findGoogleBooksCovers(
  title: string,
  author: string,
): Promise<BookCoverCandidate[]> {
  const url = new URL(GOOGLE_BOOKS_API_URL)
  url.searchParams.set('q', `intitle:"${title}" inauthor:"${author}"`)
  url.searchParams.set('printType', 'books')
  url.searchParams.set('maxResults', String(MAX_CANDIDATES))
  const apiKey = getGoogleBooksApiKey()
  if (apiKey) url.searchParams.set('key', apiKey)

  const result = await fetchJson<{ items?: GoogleVolume[] }>(url)
  const candidates: BookCoverCandidate[] = []

  for (const item of result.items ?? []) {
    const info = item.volumeInfo
    const images = info?.imageLinks
    const thumbnail = images?.thumbnail || images?.smallThumbnail
    const image = images?.large || images?.medium || images?.small || thumbnail
    if (!item.id || !info || !thumbnail || !image) continue

    candidates.push({
      source: 'googlebooks',
      sourceId: item.id,
      thumbnailUrl: httpsUrl(thumbnail),
      imageUrl: httpsUrl(image),
      title: info.title || title,
      author: info.authors?.join(', ') || author,
      publicationYear: publicationYear(info.publishedDate),
      sourceUrl: info.infoLink ? httpsUrl(info.infoLink) : `https://books.google.com/books?id=${item.id}`,
    })
  }

  return candidates
}

async function googleCoversOrError(title: string, author: string): Promise<BookCoverCandidate[]> {
  try {
    return await findGoogleBooksCovers(title, author)
  } catch (error) {
    console.warn('Google Books cover lookup failed.', error instanceof CoverServiceError ? error.status : error instanceof Error ? error.name : 'Unknown error')
    if (error instanceof CoverServiceError && error.status === 429) {
      throw new Error(getGoogleBooksApiKey()
        ? 'Google Books quota exceeded (HTTP 429). Check your API key quota and try again later.'
        : 'Google Books rejected the request (HTTP 429: no anonymous API quota). Add a Books API key in Settings.')
    }
    if (error instanceof CoverServiceError) {
      throw new Error(`Google Books cover lookup failed (HTTP ${error.status}). Check your API key and try again.`)
    }
    throw new Error('Google Books cover lookup failed. Check your connection and try again.')
  }
}

export async function findCoverCandidates(
  titleValue: string,
  authorValue: string,
  source?: 'googlebooks',
): Promise<BookCoverCandidate[]> {
  const title = titleValue.trim()
  const author = authorValue.trim()
  if (!title || !author) {
    throw new Error('Enter a title and author before looking for covers.')
  }

  if (source === 'googlebooks') return googleCoversOrError(title, author)

  try {
    const openLibraryCandidates = await findOpenLibraryCovers(title, author)
    if (openLibraryCandidates.length > 0) return openLibraryCandidates
  } catch (error) {
    console.warn('Open Library cover lookup failed; trying Google Books.', error)
  }

  return googleCoversOrError(title, author)
}

function isAllowedImageUrl(url: URL, source: BookCoverSource): boolean {
  if (url.protocol !== 'https:') return false
  if (source === 'openlibrary') return url.hostname === 'covers.openlibrary.org'
  return url.hostname === 'books.google.com'
}

function isAllowedImageRedirect(url: URL, source: BookCoverSource): boolean {
  if (url.protocol !== 'https:') return false
  if (source === 'openlibrary') {
    return url.hostname === 'covers.openlibrary.org' || url.hostname.endsWith('.archive.org')
  }
  return (
    url.hostname === 'books.google.com' ||
    url.hostname === 'books.googleusercontent.com' ||
    url.hostname.endsWith('.googleusercontent.com')
  )
}

function extensionFor(contentType: string): string | null {
  if (contentType.includes('image/jpeg')) return '.jpg'
  if (contentType.includes('image/png')) return '.png'
  if (contentType.includes('image/webp')) return '.webp'
  return null
}

export async function saveCoverLocally(
  selection: BookCoverSelection,
): Promise<SavedBookCover> {
  const requestedUrl = new URL(selection.imageUrl)
  if (!isAllowedImageUrl(requestedUrl, selection.source)) {
    throw new Error('The selected cover URL is not allowed.')
  }

  const response = await fetch(requestedUrl, {
    signal: AbortSignal.timeout(REQUEST_TIMEOUT_MS),
  })
  if (!response.ok) {
    throw new Error(`Could not download the selected cover (${response.status}).`)
  }

  const finalUrl = new URL(response.url)
  if (!isAllowedImageRedirect(finalUrl, selection.source)) {
    throw new Error('The cover download redirected to an unexpected host.')
  }

  const extension = extensionFor(response.headers.get('content-type') ?? '')
  if (!extension) {
    throw new Error('The cover service did not return a supported image.')
  }

  const declaredSize = Number(response.headers.get('content-length') ?? 0)
  if (declaredSize > MAX_COVER_BYTES) {
    throw new Error('The selected cover is too large.')
  }

  const image = Buffer.from(await response.arrayBuffer())
  if (image.byteLength > MAX_COVER_BYTES) {
    throw new Error('The selected cover is too large.')
  }

  const coversDirectory = getCoversDirectory()
  await mkdir(coversDirectory, { recursive: true })
  const filename = `${randomUUID()}${extension}`
  await writeFile(path.join(coversDirectory, filename), image, { flag: 'wx' })

  return {
    source: selection.source,
    sourceId: selection.sourceId,
    path: path.join('covers', filename),
  }
}

export async function deleteSavedCover(cover: SavedBookCover): Promise<void> {
  await rm(path.join(getDataDirectory(), cover.path), { force: true })
}
