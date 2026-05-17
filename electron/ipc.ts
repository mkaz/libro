import { ipcMain } from 'electron'

import { getDatabase, getDbInfo } from './db/client'
import { addBookReview, searchBooks } from './db/books'
import { getAuthorCounts, getReviews, getYearCounts } from './db/reports'
import { addBooksToList, createList, getAllLists, getListById } from './db/lists'

export function registerIpcHandlers(): void {
  ipcMain.handle('app:get-db-info', () => getDbInfo())

  ipcMain.handle('books:add-book-review', (_, input) =>
    addBookReview(getDatabase(), input),
  )
  ipcMain.handle('books:search', (_, term: string, listId?: number) =>
    searchBooks(getDatabase(), term, listId),
  )

  ipcMain.handle('reports:get-year-counts', () => getYearCounts(getDatabase()))
  ipcMain.handle('reports:get-author-counts', (_, minimumBooks?: number) =>
    getAuthorCounts(getDatabase(), minimumBooks),
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
}
