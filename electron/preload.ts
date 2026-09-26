import { contextBridge, ipcRenderer } from 'electron'

import type { LibroApi } from '../shared/types'

const api: LibroApi = {
  app: {
    getSettings: () => ipcRenderer.invoke('app:get-settings'),
    setDefaultView: (view) => ipcRenderer.invoke('app:set-default-view', view),
    setGoogleBooksApiKey: (key) => ipcRenderer.invoke('app:set-google-books-api-key', key),
    chooseDataDirectory: () => ipcRenderer.invoke('app:choose-data-directory'),
  },
  books: {
    findCoverCandidates: (title, author, source) =>
      ipcRenderer.invoke('books:find-cover-candidates', title, author, source),
    addBookReview: (input) => ipcRenderer.invoke('books:add-book-review', input),
    addBookCover: (input) => ipcRenderer.invoke('books:add-cover', input),
    updateReview: (input) => ipcRenderer.invoke('books:update-review', input),
    searchBooks: (term, listId) => ipcRenderer.invoke('books:search', term, listId),
    getBookDetail: (bookId) => ipcRenderer.invoke('books:get-detail', bookId),
  },
  reports: {
    getYearCounts: () => ipcRenderer.invoke('reports:get-year-counts'),
    getAuthorCounts: (minimumBooks, includeUndated) =>
      ipcRenderer.invoke('reports:get-author-counts', minimumBooks, includeUndated),
    getReviews: (filters) => ipcRenderer.invoke('reports:get-reviews', filters),
  },
  lists: {
    getAll: () => ipcRenderer.invoke('lists:get-all'),
    getById: (listId) => ipcRenderer.invoke('lists:get-by-id', listId),
    create: (input) => ipcRenderer.invoke('lists:create', input),
    addBooks: (input) => ipcRenderer.invoke('lists:add-books', input),
    addNewBook: (input) => ipcRenderer.invoke('lists:add-new-book', input),
  },
}

contextBridge.exposeInMainWorld('libro', api)
