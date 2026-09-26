import type Database from 'better-sqlite3'

import type {
  AddBookReviewInput,
  AddBookReviewResult,
  BookCoverSource,
  BookDetail,
  BookReviewDetail,
  SearchBookResult,
  UpdateReviewInput,
} from '../../shared/types'

function normalizeOptionalText(value: string | null): string | null {
  if (value === null) {
    return null
  }

  const normalized = value.trim()
  return normalized.length > 0 ? normalized : null
}

export interface SavedBookCover {
  source: BookCoverSource
  sourceId: string
  path: string
}

export function addBookReview(
  db: Database.Database,
  input: AddBookReviewInput,
  cover: SavedBookCover | null = null,
): AddBookReviewResult {
  const title = input.title.trim()
  const author = input.author.trim()
  const genre = normalizeOptionalText(input.genre)?.toLowerCase() ?? null
  const reviewText = normalizeOptionalText(input.review)

  if (!title || !author) {
    throw new Error('Title and author are required.')
  }

  const existingBook = db
    .prepare(
      `SELECT id, cover_path as coverPath
       FROM books
       WHERE LOWER(title) = LOWER(?) AND LOWER(author) = LOWER(?)`,
    )
    .get(title, author) as { id: number; coverPath: string | null } | undefined

  const insertBook = db.prepare(
    `INSERT INTO books (
       title, author, pub_year, pages, genre,
       cover_source, cover_source_id, cover_path
     )
     VALUES (?, ?, ?, ?, ?, ?, ?, ?)`,
  )
  const insertReview = db.prepare(
    `INSERT INTO reviews (book_id, date_read, rating, review)
     VALUES (?, ?, ?, ?)`,
  )
  const updateMissingCover = db.prepare(
    `UPDATE books
     SET cover_source = ?, cover_source_id = ?, cover_path = ?
     WHERE id = ? AND cover_path IS NULL`,
  )

  const transaction = db.transaction(() => {
    let bookId = existingBook?.id

    if (bookId === undefined) {
      const bookResult = insertBook.run(
        title,
        author,
        input.pubYear,
        input.pages,
        genre,
        cover?.source ?? null,
        cover?.sourceId ?? null,
        cover?.path ?? null,
      )
      bookId = Number(bookResult.lastInsertRowid)
    } else if (cover && existingBook && existingBook.coverPath === null) {
      updateMissingCover.run(cover.source, cover.sourceId, cover.path, bookId)
    }

    const reviewResult = insertReview.run(
      bookId,
      input.dateRead,
      input.rating,
      reviewText,
    )

    return {
      bookId,
      reviewId: Number(reviewResult.lastInsertRowid),
      usedExistingBook: existingBook !== undefined,
      coverSaved: cover !== null && (existingBook === undefined || existingBook.coverPath === null),
    }
  })

  return transaction()
}

export function updateReview(
  db: Database.Database,
  input: UpdateReviewInput,
): void {
  const reviewText = normalizeOptionalText(input.review)

  const result = db
    .prepare(
      `UPDATE reviews
       SET date_read = ?, rating = ?, review = ?
       WHERE id = ?`,
    )
    .run(input.dateRead, input.rating, reviewText, input.reviewId)

  if (result.changes === 0) {
    throw new Error(`Review ${input.reviewId} not found.`)
  }
}

export function addBookCover(
  db: Database.Database,
  bookId: number,
  cover: SavedBookCover,
): boolean {
  const result = db
    .prepare(
      `UPDATE books
       SET cover_source = ?, cover_source_id = ?, cover_path = ?
       WHERE id = ? AND cover_path IS NULL`,
    )
    .run(cover.source, cover.sourceId, cover.path, bookId)

  if (result.changes === 1) return true

  const bookExists = db.prepare('SELECT 1 FROM books WHERE id = ?').get(bookId)
  if (!bookExists) throw new Error(`Book ${bookId} not found.`)
  return false
}

export function getBookCoverPath(
  db: Database.Database,
  bookId: number,
): string | null {
  const row = db
    .prepare('SELECT cover_path as coverPath FROM books WHERE id = ?')
    .get(bookId) as { coverPath: string | null } | undefined
  return row?.coverPath ?? null
}

export function getBookDetail(
  db: Database.Database,
  bookId: number,
): BookDetail {
  const book = db
    .prepare(
      `SELECT
         id,
         title,
         author,
         pub_year as pubYear,
         pages,
         genre,
         cover_path IS NOT NULL as hasCover
       FROM books
       WHERE id = ?`,
    )
    .get(bookId) as (Omit<BookDetail, 'reviews' | 'hasCover'> & { hasCover: number }) | undefined

  if (!book) {
    throw new Error(`Book ${bookId} not found.`)
  }

  const reviews = db
    .prepare(
      `SELECT
         id as reviewId,
         date_read as dateRead,
         rating,
         review
       FROM reviews
       WHERE book_id = ?
       ORDER BY date_read DESC, id DESC`,
    )
    .all(bookId) as BookReviewDetail[]

  return { ...book, hasCover: Boolean(book.hasCover), reviews }
}

export function searchBooks(
  db: Database.Database,
  term: string,
  listId?: number,
): SearchBookResult[] {
  const searchTerm = term.trim()

  if (!searchTerm) {
    return db
      .prepare(
        `SELECT
           b.id,
           b.title,
           b.author,
           b.pub_year as pubYear,
           b.pages,
           b.genre,
           CASE WHEN rlb.book_id IS NOT NULL THEN 1 ELSE 0 END as inList
         FROM books b
         LEFT JOIN reading_list_books rlb
           ON rlb.book_id = b.id AND rlb.list_id = ?
         ORDER BY b.id DESC
         LIMIT 20`,
      )
      .all(listId ?? -1) as SearchBookResult[]
  }

  return db
    .prepare(
      `SELECT
         b.id,
         b.title,
         b.author,
         b.pub_year as pubYear,
         b.pages,
         b.genre,
         CASE WHEN rlb.book_id IS NOT NULL THEN 1 ELSE 0 END as inList
       FROM books b
       LEFT JOIN reading_list_books rlb
         ON rlb.book_id = b.id AND rlb.list_id = ?
       WHERE LOWER(b.title) LIKE LOWER(?) OR LOWER(b.author) LIKE LOWER(?)
       ORDER BY LOWER(b.title), LOWER(b.author)
       LIMIT 25`,
    )
    .all(listId ?? -1, `%${searchTerm}%`, `%${searchTerm}%`)
    .map((row) => ({
      ...(row as Omit<SearchBookResult, 'inList'>),
      inList: Boolean((row as { inList: number }).inList),
    }))
}
