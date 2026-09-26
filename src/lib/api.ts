import type {
  AddBookCoverInput,
  AddBookReviewInput,
  AddBooksToListInput,
  AddNewBookToListInput,
  CreateListInput,
  LibroApi,
  ReviewFilters,
  ResultView,
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
    getSettings: () => getApi().app.getSettings(),
    setDefaultView: (view: ResultView) => getApi().app.setDefaultView(view),
    setGoogleBooksApiKey: (key: string) => getApi().app.setGoogleBooksApiKey(key),
    chooseDataDirectory: () => getApi().app.chooseDataDirectory(),
  },
  books: {
    findCoverCandidates: (title: string, author: string, source?: 'googlebooks') =>
      getApi().books.findCoverCandidates(title, author, source),
    addBookReview: (input: AddBookReviewInput) => getApi().books.addBookReview(input),
    addBookCover: (input: AddBookCoverInput) => getApi().books.addBookCover(input),
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
    addNewBook: (input: AddNewBookToListInput) => getApi().lists.addNewBook(input),
  },
}
