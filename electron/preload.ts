import { contextBridge, ipcRenderer } from 'electron'

import type { LibroApi } from '../shared/types'

const api: LibroApi = {
  app: {
    getDbInfo: () => ipcRenderer.invoke('app:get-db-info'),
  },
  books: {
    addBookReview: (input) => ipcRenderer.invoke('books:add-book-review', input),
    searchBooks: (term, listId) => ipcRenderer.invoke('books:search', term, listId),
  },
  reports: {
    getYearCounts: () => ipcRenderer.invoke('reports:get-year-counts'),
    getAuthorCounts: (minimumBooks) =>
      ipcRenderer.invoke('reports:get-author-counts', minimumBooks),
    getReviews: (filters) => ipcRenderer.invoke('reports:get-reviews', filters),
  },
  lists: {
    getAll: () => ipcRenderer.invoke('lists:get-all'),
    getById: (listId) => ipcRenderer.invoke('lists:get-by-id', listId),
    create: (input) => ipcRenderer.invoke('lists:create', input),
    addBooks: (input) => ipcRenderer.invoke('lists:add-books', input),
  },
}

contextBridge.exposeInMainWorld('libro', api)
