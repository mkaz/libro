import type Database from 'better-sqlite3'

import type { AuthorCount, ReviewFilters, ReviewRow, YearCount } from '../../shared/types'

export function getYearCounts(db: Database.Database): YearCount[] {
  return db
    .prepare(
      `SELECT strftime('%Y', date_read) as year, COUNT(*) as count
       FROM reviews
       WHERE date_read IS NOT NULL
       GROUP BY year
       ORDER BY year`,
    )
    .all() as YearCount[]
}

export function getAuthorCounts(
  db: Database.Database,
  minimumBooks = 3,
  includeUndated = false,
): AuthorCount[] {
  return db
    .prepare(
      `SELECT b.author as author, COUNT(*) as count
       FROM reviews r
       JOIN books b ON r.book_id = b.id
       WHERE (? = 1 OR r.date_read IS NOT NULL)
       GROUP BY b.author
       HAVING count >= ?
       ORDER BY count DESC, LOWER(b.author) ASC`,
    )
    .all(includeUndated ? 1 : 0, minimumBooks) as AuthorCount[]
}

export function getReviews(
  db: Database.Database,
  filters: ReviewFilters = {},
): ReviewRow[] {
  let query = `
    SELECT
      r.id as reviewId,
      b.id as bookId,
      b.title,
      b.author,
      b.genre,
      r.rating,
      r.date_read as dateRead
    FROM reviews r
    JOIN books b ON r.book_id = b.id
  `

  const whereClauses: string[] = []
  const params: Array<number | string> = []

  if (filters.year !== undefined) {
    whereClauses.push(`strftime('%Y', r.date_read) = ?`)
    params.push(String(filters.year))
  }

  if (filters.author !== undefined && filters.author.trim()) {
    whereClauses.push('LOWER(b.author) LIKE LOWER(?)')
    params.push(`%${filters.author.trim()}%`)
  }

  if (filters.rating !== undefined) {
    whereClauses.push('r.rating = ?')
    params.push(filters.rating)
  }

  if (whereClauses.length > 0) {
    query += ` WHERE ${whereClauses.join(' AND ')}`
  }

  query += ' ORDER BY r.date_read DESC, r.id DESC'

  return db.prepare(query).all(...params) as ReviewRow[]
}
