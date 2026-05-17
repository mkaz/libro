export interface DbInfo {
  path: string
  exists: boolean
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
}

export interface AddBookReviewResult {
  bookId: number
  reviewId: number
  usedExistingBook: boolean
}

export interface ReviewRow {
  reviewId: number
  bookId: number
  title: string
  author: string
  genre: string | null
  rating: number | null
  dateRead: string | null
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

export interface LibroApi {
  app: {
    getDbInfo: () => Promise<DbInfo>
  }
  books: {
    addBookReview: (input: AddBookReviewInput) => Promise<AddBookReviewResult>
    searchBooks: (term: string, listId?: number) => Promise<SearchBookResult[]>
  }
  reports: {
    getYearCounts: () => Promise<YearCount[]>
    getAuthorCounts: (minimumBooks?: number) => Promise<AuthorCount[]>
    getReviews: (filters?: ReviewFilters) => Promise<ReviewRow[]>
  }
  lists: {
    getAll: () => Promise<ReadingListSummary[]>
    getById: (listId: number) => Promise<ReadingListDetail>
    create: (input: CreateListInput) => Promise<ReadingListSummary>
    addBooks: (input: AddBooksToListInput) => Promise<AddBooksToListResult>
  }
}
