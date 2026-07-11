import type {
  AddBookReviewInput,
  AddBooksToListInput,
  CreateListInput,
  LibroApi,
  ReviewFilters,
  UpdateReviewInput,
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
    updateReview: (input: UpdateReviewInput) => getApi().books.updateReview(input),
    searchBooks: (term: string, listId?: number) => getApi().books.searchBooks(term, listId),
    getBookDetail: (bookId: number) => getApi().books.getBookDetail(bookId),
  },
  reports: {
    getYearCounts: () => getApi().reports.getYearCounts(),
    getAuthorCounts: (minimumBooks?: number, includeUndated?: boolean) => getApi().reports.getAuthorCounts(minimumBooks, includeUndated),
    getReviews: (filters?: ReviewFilters) => getApi().reports.getReviews(filters),
  },
  lists: {
    getAll: () => getApi().lists.getAll(),
    getById: (listId: number) => getApi().lists.getById(listId),
    create: (input: CreateListInput) => getApi().lists.create(input),
    addBooks: (input: AddBooksToListInput) => getApi().lists.addBooks(input),
  },
}
