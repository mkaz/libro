import { useDeferredValue, useEffect, useMemo, useRef, useState } from 'react'

import type {
  AddNewBookToListInput,
  ReadingListBookRow,
  ReadingListDetail,
  ReadingListSummary,
  SearchBookResult,
} from '../../../shared/types'

type SortKey = 'title' | 'author' | 'genre' | 'pubYear' | 'rating'
import { api } from '../../lib/api'
import { starsFor } from '../../lib/ratings'

function ProgressBar({ percentage }: { percentage: number }) {
  return (
    <div>
      <div className="progress reading-progress mb-5">
        <div className="progress-bar" style={{ width: `${percentage}%` }} />
      </div>
      <small className="text-muted">{percentage.toFixed(1)}% complete</small>
    </div>
  )
}

function toOptionalNumber(value: string): number | null {
  return value.trim() ? Number(value) : null
}

const initialNewBookForm: Omit<AddNewBookToListInput, 'listId'> = {
  title: '',
  author: '',
  pubYear: null,
  pages: null,
  genre: null,
}

function AddNewBookModal({
  onClose,
  onAdd,
}: {
  onClose: () => void
  onAdd: (input: Omit<AddNewBookToListInput, 'listId'>) => Promise<void>
}) {
  const [form, setForm] = useState(initialNewBookForm)
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    inputRef.current?.focus()
  }, [])

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setSubmitting(true)
    setError(null)

    try {
      await onAdd({
        ...form,
        title: form.title.trim(),
        author: form.author.trim(),
        genre: form.genre?.trim() || null,
      })
      onClose()
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to add book.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="modal-overlay" onClick={onClose} role="dialog" aria-modal="true">
      <div className="modal-box" onClick={(event) => event.stopPropagation()}>
        <h3 className="modal-title">Add New Book</h3>
        <p className="text-muted mb-20">Add an unread book directly to this list.</p>
        {error ? <div className="alert alert-danger mb-15">{error}</div> : null}
        <form className="row g-20" onSubmit={(event) => void handleSubmit(event)}>
          <div className="col-12">
            <label className="form-label" htmlFor="listBookTitle">
              Title
            </label>
            <input
              ref={inputRef}
              id="listBookTitle"
              className="form-control"
              value={form.title}
              onChange={(event) => setForm((current) => ({ ...current, title: event.target.value }))}
              required
            />
          </div>
          <div className="col-12">
            <label className="form-label" htmlFor="listBookAuthor">
              Author
            </label>
            <input
              id="listBookAuthor"
              className="form-control"
              value={form.author}
              onChange={(event) => setForm((current) => ({ ...current, author: event.target.value }))}
              required
            />
          </div>
          <div className="col-12 col-md-6">
            <label className="form-label" htmlFor="listBookPubYear">
              Publication year
            </label>
            <input
              id="listBookPubYear"
              className="form-control"
              inputMode="numeric"
              value={form.pubYear ?? ''}
              onChange={(event) =>
                setForm((current) => ({ ...current, pubYear: toOptionalNumber(event.target.value) }))
              }
            />
          </div>
          <div className="col-12 col-md-6">
            <label className="form-label" htmlFor="listBookPages">
              Pages
            </label>
            <input
              id="listBookPages"
              className="form-control"
              inputMode="numeric"
              value={form.pages ?? ''}
              onChange={(event) =>
                setForm((current) => ({ ...current, pages: toOptionalNumber(event.target.value) }))
              }
            />
          </div>
          <div className="col-12">
            <label className="form-label" htmlFor="listBookGenre">
              Genre
            </label>
            <input
              id="listBookGenre"
              className="form-control"
              value={form.genre ?? ''}
              onChange={(event) => setForm((current) => ({ ...current, genre: event.target.value }))}
            />
          </div>
          <div className="col-12 modal-actions">
            <button type="button" className="btn" onClick={onClose} disabled={submitting}>
              Cancel
            </button>
            <button type="submit" className="btn btn-primary" disabled={submitting}>
              {submitting ? 'Adding...' : 'Add book'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

function CreateListModal({
  onClose,
  onCreate,
}: {
  onClose: () => void
  onCreate: (name: string) => Promise<void>
}) {
  const [name, setName] = useState('')
  const [error, setError] = useState<string | null>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    inputRef.current?.focus()
  }, [])

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError(null)
    try {
      await onCreate(name)
      onClose()
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to create list.')
    }
  }

  return (
    <div className="modal-overlay" onClick={onClose} role="dialog" aria-modal="true">
      <div className="modal-box" onClick={(e) => e.stopPropagation()}>
        <h3 className="modal-title">New Reading List</h3>
        {error ? <div className="alert alert-danger mb-15">{error}</div> : null}
        <form onSubmit={(e) => void handleSubmit(e)}>
          <label className="form-label" htmlFor="newListName">
            List name
          </label>
          <input
            ref={inputRef}
            id="newListName"
            className="form-control mb-20"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
          />
          <div className="modal-actions">
            <button type="button" className="btn" onClick={onClose}>
              Cancel
            </button>
            <button type="submit" className="btn btn-primary">
              Create list
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export function ListsView() {
  const [lists, setLists] = useState<ReadingListSummary[]>([])
  const [selectedListId, setSelectedListId] = useState<number | null>(null)
  const [selectedList, setSelectedList] = useState<ReadingListDetail | null>(null)
  const [searchTerm, setSearchTerm] = useState('')
  const deferredSearchTerm = useDeferredValue(searchTerm)
  const [searchResults, setSearchResults] = useState<SearchBookResult[]>([])
  const [selectedBookIds, setSelectedBookIds] = useState<number[]>([])
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [showAddNewBookModal, setShowAddNewBookModal] = useState(false)
  const [message, setMessage] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [sortKey, setSortKey] = useState<SortKey>('title')
  const [sortDir, setSortDir] = useState<'asc' | 'desc'>('asc')

  function handleSort(key: SortKey) {
    if (key === sortKey) {
      setSortDir((d) => (d === 'asc' ? 'desc' : 'asc'))
    } else {
      setSortKey(key)
      setSortDir('asc')
    }
  }

  const sortedBooks = useMemo(() => {
    if (!selectedList) return []
    return [...selectedList.books].sort((a, b) => {
      const av: string = String((a as ReadingListBookRow)[sortKey] ?? '')
      const bv: string = String((b as ReadingListBookRow)[sortKey] ?? '')
      const cmp = av.localeCompare(bv, undefined, { numeric: true })
      return sortDir === 'asc' ? cmp : -cmp
    })
  }, [selectedList, sortKey, sortDir])

  async function loadLists(preferredListId?: number) {
    const nextLists = await api.lists.getAll()
    setLists(nextLists)

    const resolvedListId =
      preferredListId ??
      (selectedListId !== null && nextLists.some((list) => list.id === selectedListId)
        ? selectedListId
        : nextLists[0]?.id ?? null)

    setSelectedListId(resolvedListId)
  }

  async function loadListDetail(listId: number) {
    const detail = await api.lists.getById(listId)
    setSelectedList(detail)
  }

  useEffect(() => {
    void api.lists
      .getAll()
      .then((nextLists) => {
        setLists(nextLists)
        setSelectedListId(nextLists[0]?.id ?? null)
      })
      .catch((loadError: unknown) => {
        setError(loadError instanceof Error ? loadError.message : 'Failed to load reading lists.')
      })
  }, [])

  useEffect(() => {
    if (selectedListId === null) {
      setSelectedList(null)
      return
    }

    void loadListDetail(selectedListId).catch((loadError: unknown) => {
      setError(loadError instanceof Error ? loadError.message : 'Failed to load list details.')
    })
  }, [selectedListId])

  useEffect(() => {
    if (selectedListId === null || !deferredSearchTerm.trim()) {
      setSearchResults([])
      return
    }

    void api.books
      .searchBooks(deferredSearchTerm, selectedListId)
      .then(setSearchResults)
      .catch((loadError: unknown) => {
        setError(loadError instanceof Error ? loadError.message : 'Failed to search books.')
      })
  }, [deferredSearchTerm, selectedListId])

  async function handleCreateList(name: string) {
    const created = await api.lists.create({ name, description: null })
    setMessage(`Created "${created.name}".`)
    await loadLists(created.id)
  }

  async function handleAddNewBook(input: Omit<AddNewBookToListInput, 'listId'>) {
    if (selectedListId === null) {
      return
    }

    setError(null)
    setMessage(null)

    const result = await api.lists.addNewBook({ ...input, listId: selectedListId })
    setMessage(
      result.usedExistingBook
        ? 'Existing book added to the list.'
        : 'New unread book added to the list.',
    )
    await loadLists(selectedListId)
    await loadListDetail(selectedListId)
  }

  async function handleAddBooks() {
    if (selectedListId === null || selectedBookIds.length === 0) {
      return
    }

    setError(null)
    setMessage(null)

    try {
      const result = await api.lists.addBooks({
        listId: selectedListId,
        bookIds: selectedBookIds,
      })
      setMessage(
        result.skippedBookIds.length > 0
          ? `Added ${result.addedCount} book(s). Skipped ${result.skippedBookIds.length} already in list.`
          : `Added ${result.addedCount} book(s) to the list.`,
      )
      setSelectedBookIds([])
      setSearchTerm('')
      await loadLists(selectedListId)
      await loadListDetail(selectedListId)
    } catch (addError: unknown) {
      setError(addError instanceof Error ? addError.message : 'Failed to add books to list.')
    }
  }

  return (
    <section className="lists-layout">
      {showCreateModal ? (
        <CreateListModal
          onClose={() => setShowCreateModal(false)}
          onCreate={handleCreateList}
        />
      ) : null}
      {showAddNewBookModal ? (
        <AddNewBookModal
          onClose={() => setShowAddNewBookModal(false)}
          onAdd={handleAddNewBook}
        />
      ) : null}

      {/* Left column: list selector */}
      <div className="card section-card">
        <div className="card-body">
          <div className="section-heading">
            <h2 className="section-title mb-0">Reading Lists</h2>
            <button
              type="button"
              className="btn btn-primary"
              onClick={() => {
                setMessage(null)
                setError(null)
                setShowCreateModal(true)
              }}
            >
              + New List
            </button>
          </div>

          {message ? <div className="alert alert-success mb-15">{message}</div> : null}
          {error ? <div className="alert alert-danger mb-15">{error}</div> : null}

          <div className="list-summary-stack">
            {lists.length === 0 ? (
              <p className="text-muted mb-0">No reading lists yet.</p>
            ) : null}
            {lists.map((list) => (
              <button
                key={list.id}
                type="button"
                className={`list-summary-card ${selectedListId === list.id ? 'is-active' : ''}`}
                onClick={() => setSelectedListId(list.id)}
              >
                <div className="d-flex justify-content-between align-items-start gap-10">
                  <strong>{list.name}</strong>
                  <span className="badge bg-secondary">{list.totalBooks} books</span>
                </div>
                <div className="list-meta-row">
                  <span>{list.booksRead} read</span>
                  <span>{list.booksUnread} unread</span>
                </div>
                <ProgressBar percentage={list.completionPercentage} />
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Right column: selected list detail */}
      <div className="card section-card list-detail-card">
        <div className="card-body">
          {selectedList ? (
            <>
              <div className="section-heading mb-5">
                <h2 className="section-title mb-0">{selectedList.name}</h2>
                <button
                  type="button"
                  className="btn btn-primary"
                  onClick={() => {
                    setMessage(null)
                    setError(null)
                    setShowAddNewBookModal(true)
                  }}
                >
                  + Add new book
                </button>
              </div>
              {selectedList.description ? (
                <p className="section-copy mb-15">{selectedList.description}</p>
              ) : null}

              <div className="list-stat-grid mb-15">
                <div className="stat-chip">
                  <span>Total books</span>
                  <strong>{selectedList.stats.totalBooks}</strong>
                </div>
                <div className="stat-chip">
                  <span>Read</span>
                  <strong>{selectedList.stats.booksRead}</strong>
                </div>
                <div className="stat-chip">
                  <span>Unread</span>
                  <strong>{selectedList.stats.booksUnread}</strong>
                </div>
                <div className="stat-chip">
                  <span>Completion</span>
                  <strong>{selectedList.stats.completionPercentage.toFixed(1)}%</strong>
                </div>
              </div>

              {selectedList.books.length > 0 ? (
                <>
                  <hr className="my-20" />
                  <div className="list-books-header">
                    <span />
                    <div className="list-book-info">
                      {(['title', 'author', 'genre', 'pubYear', 'rating'] as SortKey[]).map((key) => (
                        <button
                          key={key}
                          type="button"
                          className={`list-sort-btn ${sortKey === key ? 'is-active' : ''}`}
                          onClick={() => handleSort(key)}
                        >
                          {key === 'pubYear' ? 'Year' : key === 'rating' ? 'Rating' : key.charAt(0).toUpperCase() + key.slice(1)}
                          {sortKey === key ? (sortDir === 'asc' ? ' ↑' : ' ↓') : ''}
                        </button>
                      ))}
                    </div>
                  </div>
                  <div className="list-books-stack">
                    {sortedBooks.map((book) => (
                      <div
                        key={book.bookId}
                        className={`list-book-row ${book.isRead ? 'is-read' : 'is-unread'}`}
                      >
                        <div className="list-book-status">
                          {book.isRead ? '✓' : '○'}
                        </div>
                        <div className="list-book-info">
                          <strong className="list-book-col">{book.title}</strong>
                          <span className="list-book-col list-book-meta-text">{book.author}</span>
                          <span className="list-book-col list-book-meta-text">{book.genre ?? ''}</span>
                          <span className="list-book-col list-book-meta-text">{book.pubYear ?? ''}</span>
                          <span className="list-book-col list-book-meta-text">
                            {[
                              book.rating ? starsFor(book.rating) : null,
                              book.dateRead ? book.dateRead.slice(0, 4) : null,
                            ]
                              .filter(Boolean)
                              .join(' · ')}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </>
              ) : null}

              <hr className="my-20" />

              <div className="section-heading section-heading-inline mb-10">
                <h3 className="mb-0">Add books</h3>
                <button
                  type="button"
                  className="btn btn-primary"
                  onClick={() => void handleAddBooks()}
                  disabled={selectedBookIds.length === 0}
                >
                  Add selected ({selectedBookIds.length})
                </button>
              </div>

              <input
                className="form-control mb-10"
                placeholder="Search by title or author"
                value={searchTerm}
                onChange={(event) => setSearchTerm(event.target.value)}
              />

              {searchTerm.trim() ? (
                <div className="search-results-stack">
                  {searchResults.length === 0 ? (
                    <p className="text-muted mb-0">No books found.</p>
                  ) : (
                    searchResults.map((book) => (
                      <label
                        key={book.id}
                        className={`search-result-row ${book.inList ? 'is-disabled' : ''}`}
                      >
                        <input
                          type="checkbox"
                          checked={selectedBookIds.includes(book.id)}
                          disabled={book.inList}
                          onChange={(event) => {
                            setSelectedBookIds((current) =>
                              event.target.checked
                                ? [...current, book.id]
                                : current.filter((id) => id !== book.id),
                            )
                          }}
                        />
                        <div>
                          <strong>{book.title}</strong>
                          <p className="text-muted mb-0">
                            {book.author}
                            {book.pubYear ? ` · ${book.pubYear}` : ''}
                            {book.genre ? ` · ${book.genre}` : ''}
                          </p>
                        </div>
                        {book.inList ? (
                          <span className="badge bg-secondary">Already in list</span>
                        ) : null}
                      </label>
                    ))
                  )}
                </div>
              ) : null}
            </>
          ) : (
            <p className="text-muted mb-0">Select a list to view its details.</p>
          )}
        </div>
      </div>
    </section>
  )
}
