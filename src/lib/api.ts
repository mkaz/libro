import type {
  AddBookReviewInput,
  AddBooksToListInput,
  CreateListInput,
  LibroApi,
  ReviewFilters,
} from '../../shared/types'

function getApi(): LibroApi {
  if (!window.libro) {
    throw new Error('Electron API bridge is unavailable.')
  }

  return window.libro
}

export const api = {
  app: {
    getDbInfo: () => getApi().app.getDbInfo(),
  },
  books: {
    addBookReview: (input: AddBookReviewInput) => getApi().books.addBookReview(input),
    searchBooks: (term: string, listId?: number) => getApi().books.searchBooks(term, listId),
  },
  reports: {
    getYearCounts: () => getApi().reports.getYearCounts(),
    getAuthorCounts: (minimumBooks?: number) => getApi().reports.getAuthorCounts(minimumBooks),
    getReviews: (filters?: ReviewFilters) => getApi().reports.getReviews(filters),
  },
  lists: {
    getAll: () => getApi().lists.getAll(),
    getById: (listId: number) => getApi().lists.getById(listId),
    create: (input: CreateListInput) => getApi().lists.create(input),
    addBooks: (input: AddBooksToListInput) => getApi().lists.addBooks(input),
  },
}
