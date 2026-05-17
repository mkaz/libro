import type Database from 'better-sqlite3'

import type {
  AddBookReviewInput,
  AddBookReviewResult,
  SearchBookResult,
} from '../../shared/types'

function normalizeOptionalText(value: string | null): string | null {
  if (value === null) {
    return null
  }

  const normalized = value.trim()
  return normalized.length > 0 ? normalized : null
}

export function addBookReview(
  db: Database.Database,
  input: AddBookReviewInput,
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
      `SELECT id
       FROM books
       WHERE LOWER(title) = LOWER(?) AND LOWER(author) = LOWER(?)`,
    )
    .get(title, author) as { id: number } | undefined

  const insertBook = db.prepare(
    `INSERT INTO books (title, author, pub_year, pages, genre)
     VALUES (?, ?, ?, ?, ?)`,
  )
  const insertReview = db.prepare(
    `INSERT INTO reviews (book_id, date_read, rating, review)
     VALUES (?, ?, ?, ?)`,
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
      )
      bookId = Number(bookResult.lastInsertRowid)
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
    }
  })

  return transaction()
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
