import { ipcMain } from 'electron'

import type { AddBookCoverInput, AddBookReviewInput } from '../shared/types'
import { deleteSavedCover, findCoverCandidates, saveCoverLocally } from './covers'
import { getDatabase, getDbInfo } from './db/client'
import { addBookCover, addBookReview, getBookDetail, searchBooks, updateReview } from './db/books'
import { getAuthorCounts, getReviews, getYearCounts } from './db/reports'
import { addBooksToList, addNewBookToList, createList, getAllLists, getListById } from './db/lists'

async function addBookReviewWithCover(input: AddBookReviewInput) {
  const savedCover = input.cover ? await saveCoverLocally(input.cover) : null
  let result

  try {
    result = addBookReview(getDatabase(), input, savedCover)
  } catch (error) {
    if (savedCover) {
      await deleteSavedCover(savedCover).catch((cleanupError: unknown) => {
        console.warn('Could not remove unused cover after save failure.', cleanupError)
      })
    }
    throw error
  }

  if (!result.coverSaved && savedCover) {
    await deleteSavedCover(savedCover).catch((cleanupError: unknown) => {
      console.warn('Could not remove a cover the book did not use.', cleanupError)
    })
  }
  return result
}

async function addCoverToBook(input: AddBookCoverInput) {
  const savedCover = await saveCoverLocally(input.cover)

  try {
    const coverSaved = addBookCover(getDatabase(), input.bookId, savedCover)
    if (!coverSaved) {
      await deleteSavedCover(savedCover).catch((cleanupError: unknown) => {
        console.warn('Could not remove a cover the book did not use.', cleanupError)
      })
    }
    return { coverSaved }
  } catch (error) {
    await deleteSavedCover(savedCover).catch((cleanupError: unknown) => {
      console.warn('Could not remove unused cover after save failure.', cleanupError)
    })
    throw error
  }
}

export function registerIpcHandlers(): void {
  ipcMain.handle('app:get-db-info', () => getDbInfo())

  ipcMain.handle('books:find-cover-candidates', (_, title: string, author: string) =>
    findCoverCandidates(title, author),
  )
  ipcMain.handle('books:add-book-review', (_, input: AddBookReviewInput) =>
    addBookReviewWithCover(input),
  )
  ipcMain.handle('books:add-cover', (_, input: AddBookCoverInput) =>
    addCoverToBook(input),
  )
  ipcMain.handle('books:search', (_, term: string, listId?: number) =>
    searchBooks(getDatabase(), term, listId),
  )
  ipcMain.handle('books:get-detail', (_, bookId: number) =>
    getBookDetail(getDatabase(), bookId),
  )
  ipcMain.handle('books:update-review', (_, input) =>
    updateReview(getDatabase(), input),
  )

  ipcMain.handle('reports:get-year-counts', () => getYearCounts(getDatabase()))
  ipcMain.handle('reports:get-author-counts', (_, minimumBooks?: number, includeUndated?: boolean) =>
    getAuthorCounts(getDatabase(), minimumBooks, includeUndated),
  )
  ipcMain.handle('reports:get-reviews', (_, filters) =>
    getReviews(getDatabase(), filters),
  )

  ipcMain.handle('lists:get-all', () => getAllLists(getDatabase()))
  ipcMain.handle('lists:get-by-id', (_, listId: number) =>
    getListById(getDatabase(), listId),
  )
  ipcMain.handle('lists:create', (_, input) => createList(getDatabase(), input))
  ipcMain.handle('lists:add-books', (_, input) =>
    addBooksToList(getDatabase(), input),
  )
  ipcMain.handle('lists:add-new-book', (_, input) =>
    addNewBookToList(getDatabase(), input),
  )
}
