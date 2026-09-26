export type ResultView = 'list' | 'grid'

export interface AppSettings {
  dataDirectory: string
  defaultView: ResultView
  directoryLocked: boolean
  googleBooksApiKeySource: 'settings' | 'environment' | null
}

export type BookCoverSource = 'openlibrary' | 'googlebooks'

export interface BookCoverSelection {
  source: BookCoverSource
  sourceId: string
  imageUrl: string
}

export interface BookCoverCandidate extends BookCoverSelection {
  thumbnailUrl: string
  title: string
  author: string
  publicationYear: string | null
  sourceUrl: string
}

export interface AddBookCoverInput {
  bookId: number
  cover: BookCoverSelection
}

export interface AddBookCoverResult {
  coverSaved: boolean
}

export interface AddBookReviewInput {
  title: string
  author: string
  pubYear: number | null
  pages: number | null
  genre: string | null
  dateRead: string | null
  rating: number | null
  review: string | null
  cover: BookCoverSelection | null
}

export interface AddBookReviewResult {
  bookId: number
  reviewId: number
  usedExistingBook: boolean
  coverSaved: boolean
}

export interface UpdateReviewInput {
  reviewId: number
  dateRead: string | null
  rating: number | null
  review: string | null
}

export interface ReviewRow {
  reviewId: number
  bookId: number
  title: string
  author: string
  genre: string | null
  hasCover: boolean
  rating: number | null
  dateRead: string | null
}

export interface BookReviewDetail {
  reviewId: number
  dateRead: string | null
  rating: number | null
  review: string | null
}

export interface BookDetail {
  id: number
  title: string
  author: string
  pubYear: number | null
  pages: number | null
  genre: string | null
  hasCover: boolean
  reviews: BookReviewDetail[]
}

export interface YearCount {
  year: string
  count: number
}

export interface AuthorCount {
  author: string
  count: number
}

export interface ReviewFilters {
  year?: number
  author?: string
  rating?: number
}

export interface SearchBookResult {
  id: number
  title: string
  author: string
  pubYear: number | null
  pages: number | null
  genre: string | null
  inList: boolean
}

export interface ReadingListSummary {
  id: number
  name: string
  description: string | null
  createdDate: string | null
  totalBooks: number
  booksRead: number
  booksUnread: number
  completionPercentage: number
}

export interface ReadingListBookRow {
  bookId: number
  title: string
  author: string
  genre: string | null
  pubYear: number | null
  pages: number | null
  addedDate: string | null
  priority: number
  isRead: boolean
  dateRead: string | null
  rating: number | null
}

export interface ReadingListDetail {
  id: number
  name: string
  description: string | null
  createdDate: string | null
  books: ReadingListBookRow[]
  stats: {
    totalBooks: number
    booksRead: number
    booksUnread: number
    completionPercentage: number
  }
}

export interface CreateListInput {
  name: string
  description: string | null
}

export interface AddBooksToListInput {
  listId: number
  bookIds: number[]
}

export interface AddBooksToListResult {
  addedCount: number
  skippedBookIds: number[]
}

export interface AddNewBookToListInput {
  listId: number
  title: string
  author: string
  pubYear: number | null
  pages: number | null
  genre: string | null
}

export interface AddNewBookToListResult {
  bookId: number
  usedExistingBook: boolean
}

export interface LibroApi {
  app: {
    getSettings: () => Promise<AppSettings>
    setDefaultView: (view: ResultView) => Promise<AppSettings>
    setGoogleBooksApiKey: (key: string) => Promise<AppSettings>
    chooseDataDirectory: () => Promise<string | null>
  }
  books: {
    findCoverCandidates: (title: string, author: string, source?: 'googlebooks') => Promise<BookCoverCandidate[]>
    addBookReview: (input: AddBookReviewInput) => Promise<AddBookReviewResult>
    addBookCover: (input: AddBookCoverInput) => Promise<AddBookCoverResult>
    updateReview: (input: UpdateReviewInput) => Promise<void>
    searchBooks: (term: string, listId?: number) => Promise<SearchBookResult[]>
    getBookDetail: (bookId: number) => Promise<BookDetail>
  }
  reports: {
    getYearCounts: () => Promise<YearCount[]>
    getAuthorCounts: (minimumBooks?: number, includeUndated?: boolean) => Promise<AuthorCount[]>
    getReviews: (filters?: ReviewFilters) => Promise<ReviewRow[]>
  }
  lists: {
    getAll: () => Promise<ReadingListSummary[]>
    getById: (listId: number) => Promise<ReadingListDetail>
    create: (input: CreateListInput) => Promise<ReadingListSummary>
    addBooks: (input: AddBooksToListInput) => Promise<AddBooksToListResult>
    addNewBook: (input: AddNewBookToListInput) => Promise<AddNewBookToListResult>
  }
}
