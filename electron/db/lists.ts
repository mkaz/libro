import type Database from 'better-sqlite3'

import type {
  AddBooksToListInput,
  AddBooksToListResult,
  CreateListInput,
  ReadingListBookRow,
  ReadingListDetail,
  ReadingListSummary,
} from '../../shared/types'

type ReadingListRow = {
  id: number
  name: string
  description: string | null
  createdDate: string | null
}

type ReadingListBookStats = {
  totalBooks: number
  booksRead: number
  booksUnread: number
  completionPercentage: number
}

function hydrateStats(
  totalBooks: number,
  booksRead: number,
): ReadingListBookStats {
  const booksUnread = totalBooks - booksRead
  return {
    totalBooks,
    booksRead,
    booksUnread,
    completionPercentage: totalBooks > 0 ? (booksRead / totalBooks) * 100 : 0,
  }
}

export function getAllLists(db: Database.Database): ReadingListSummary[] {
  const rows = db
    .prepare(
      `SELECT
         rl.id,
         rl.name,
         rl.description,
         rl.created_date as createdDate,
         COUNT(DISTINCT rlb.book_id) as totalBooks,
         COUNT(DISTINCT CASE WHEN EXISTS (
           SELECT 1 FROM reviews r WHERE r.book_id = rlb.book_id
         ) THEN rlb.book_id END) as booksRead
       FROM reading_lists rl
       LEFT JOIN reading_list_books rlb ON rl.id = rlb.list_id
       GROUP BY rl.id
       ORDER BY rl.created_date DESC, LOWER(rl.name) ASC`,
    )
    .all() as Array<ReadingListRow & { totalBooks: number; booksRead: number }>

  return rows.map((row) => {
    const stats = hydrateStats(row.totalBooks, row.booksRead)
    return {
      id: row.id,
      name: row.name,
      description: row.description,
      createdDate: row.createdDate,
      ...stats,
    }
  })
}

export function getListById(
  db: Database.Database,
  listId: number,
): ReadingListDetail {
  const list = db
    .prepare(
      `SELECT id, name, description, created_date as createdDate
       FROM reading_lists
       WHERE id = ?`,
    )
    .get(listId) as ReadingListRow | undefined

  if (!list) {
    throw new Error(`Reading list with ID ${listId} not found.`)
  }

  const books = db
    .prepare(
      `SELECT
         b.id as bookId,
         b.title,
         b.author,
         b.genre,
         b.pub_year as pubYear,
         b.pages,
         rlb.added_date as addedDate,
         rlb.priority,
         CASE WHEN EXISTS (
           SELECT 1 FROM reviews r WHERE r.book_id = b.id
         ) THEN 1 ELSE 0 END as isRead,
         (
           SELECT r.date_read
           FROM reviews r
           WHERE r.book_id = b.id
           ORDER BY COALESCE(r.date_read, '') DESC, r.id DESC
           LIMIT 1
         ) as dateRead,
         (
           SELECT r.rating
           FROM reviews r
           WHERE r.book_id = b.id
           ORDER BY COALESCE(r.date_read, '') DESC, r.id DESC
           LIMIT 1
         ) as rating
       FROM reading_list_books rlb
       JOIN books b ON rlb.book_id = b.id
       WHERE rlb.list_id = ?
       ORDER BY isRead ASC, rlb.priority DESC, rlb.added_date ASC, LOWER(b.title) ASC`,
    )
    .all(listId)
    .map((row) => ({
      ...(row as Omit<ReadingListBookRow, 'isRead'>),
      isRead: Boolean((row as { isRead: number }).isRead),
    })) as ReadingListBookRow[]

  const booksRead = books.filter((book) => book.isRead).length
  const stats = hydrateStats(books.length, booksRead)

  return {
    id: list.id,
    name: list.name,
    description: list.description,
    createdDate: list.createdDate,
    books,
    stats,
  }
}

export function createList(
  db: Database.Database,
  input: CreateListInput,
): ReadingListSummary {
  const name = input.name.trim()
  const description = input.description?.trim() || null

  if (!name) {
    throw new Error('List name is required.')
  }

  const existing = db
    .prepare('SELECT id FROM reading_lists WHERE name = ?')
    .get(name) as { id: number } | undefined

  if (existing) {
    throw new Error(`A reading list named "${name}" already exists.`)
  }

  const result = db
    .prepare(
      `INSERT INTO reading_lists (name, description, created_date)
       VALUES (?, ?, CURRENT_DATE)`,
    )
    .run(name, description)

  const createdId = Number(result.lastInsertRowid)
  return getAllLists(db).find((list) => list.id === createdId) ?? {
    id: createdId,
    name,
    description,
    createdDate: null,
    ...hydrateStats(0, 0),
  }
}

export function addBooksToList(
  db: Database.Database,
  input: AddBooksToListInput,
): AddBooksToListResult {
  const list = db
    .prepare('SELECT id FROM reading_lists WHERE id = ?')
    .get(input.listId) as { id: number } | undefined

  if (!list) {
    throw new Error(`Reading list with ID ${input.listId} not found.`)
  }

  const existingBookIds = new Set<number>(
    (
      db
        .prepare(
          `SELECT id
           FROM books
           WHERE id IN (${input.bookIds.map(() => '?').join(', ') || 'NULL'})`,
        )
        .all(...input.bookIds) as Array<{ id: number }>
    ).map((row) => row.id),
  )

  const insert = db.prepare(
    `INSERT OR IGNORE INTO reading_list_books (list_id, book_id, added_date, priority)
     VALUES (?, ?, CURRENT_DATE, 0)`,
  )

  let addedCount = 0
  const skippedBookIds: number[] = []

  const transaction = db.transaction(() => {
    for (const bookId of input.bookIds) {
      if (!existingBookIds.has(bookId)) {
        skippedBookIds.push(bookId)
        continue
      }

      const result = insert.run(input.listId, bookId)
      if (result.changes === 1) {
        addedCount += 1
      } else {
        skippedBookIds.push(bookId)
      }
    }
  })

  transaction()

  return {
    addedCount,
    skippedBookIds,
  }
}
