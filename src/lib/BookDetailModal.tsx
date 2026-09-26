import { useEffect, useState } from 'react'

import type { BookCoverCandidate, BookDetail, BookReviewDetail } from '../../shared/types'
import { api } from './api'
import { BookCover } from './BookCover'
import { starsFor } from './ratings'
import { StarRating } from './StarRating'

export function BookDetailModal({
  bookId,
  onClose,
  onCoverSaved,
}: {
  bookId: number
  onClose: () => void
  onCoverSaved?: () => void
}) {
  const [book, setBook] = useState<BookDetail | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [choosingCover, setChoosingCover] = useState(false)

  function loadBook() {
    void api.books
      .getBookDetail(bookId)
      .then(setBook)
      .catch((loadError: unknown) => {
        setError(loadError instanceof Error ? loadError.message : 'Failed to load book.')
      })
  }

  useEffect(() => {
    loadBook()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [bookId])

  useEffect(() => {
    function handleKey(event: KeyboardEvent) {
      if (event.key === 'Escape') {
        if (choosingCover) setChoosingCover(false)
        else onClose()
      }
    }
    window.addEventListener('keydown', handleKey)
    return () => window.removeEventListener('keydown', handleKey)
  }, [choosingCover, onClose])

  return (
    <div className="modal-overlay" onClick={onClose} role="dialog" aria-modal="true">
      <div
        className="modal-box modal-box-wide"
        onClick={(e) => e.stopPropagation()}
      >
        {error ? <div className="alert alert-danger">{error}</div> : null}
        {!book && !error ? <p className="text-muted mb-0">Loading…</p> : null}
        {book && choosingCover ? (
          <ExistingBookCoverPicker
            book={book}
            onCancel={() => setChoosingCover(false)}
            onSaved={() => {
              setChoosingCover(false)
              loadBook()
              onCoverSaved?.()
            }}
          />
        ) : book ? (
          <>
            <div className="book-detail-layout">
              {book.hasCover ? (
                <BookCover
                  bookId={book.id}
                  title={book.title}
                  hasCover
                  className="book-detail-cover"
                />
              ) : (
                <button
                  type="button"
                  className="book-detail-cover-button"
                  onClick={() => setChoosingCover(true)}
                  aria-label={`Add a cover for ${book.title}`}
                  title="Add cover"
                >
                  <BookCover
                    bookId={book.id}
                    title={book.title}
                    hasCover={false}
                    className="book-detail-cover"
                  />
                  <span>Click to add</span>
                </button>
              )}
              <div className="book-detail-main">
                <div className="book-detail-header">
                  <h3 className="modal-title mb-0">{book.title}</h3>
                  <button
                    type="button"
                    className="btn btn-sm"
                    onClick={onClose}
                    aria-label="Close"
                  >
                    ✕
                  </button>
                </div>
                <p className="book-detail-author">{book.author}</p>
                <dl className="book-detail-meta">
                  {book.pubYear !== null ? (
                    <div>
                      <dt>Published</dt>
                      <dd>{book.pubYear}</dd>
                    </div>
                  ) : null}
                  {book.pages !== null ? (
                    <div>
                      <dt>Pages</dt>
                      <dd>{book.pages}</dd>
                    </div>
                  ) : null}
                  {book.genre ? (
                    <div>
                      <dt>Genre</dt>
                      <dd>{book.genre}</dd>
                    </div>
                  ) : null}
                </dl>
              </div>
            </div>

            <h4 className="book-detail-subtitle">
              {book.reviews.length === 1 ? 'Review' : 'Reviews'}
            </h4>
            {book.reviews.length === 0 ? (
              <p className="text-muted mb-0">No reviews yet.</p>
            ) : (
              <div className="book-detail-reviews">
                {book.reviews.map((review) => (
                  <ReviewItem
                    key={review.reviewId}
                    review={review}
                    onSaved={loadBook}
                  />
                ))}
              </div>
            )}
          </>
        ) : null}
      </div>
    </div>
  )
}

function ExistingBookCoverPicker({
  book,
  onCancel,
  onSaved,
}: {
  book: BookDetail
  onCancel: () => void
  onSaved: () => void
}) {
  const [candidates, setCandidates] = useState<BookCoverCandidate[] | null>(null)
  const [googleCandidates, setGoogleCandidates] = useState<BookCoverCandidate[] | null>(null)
  const [googleError, setGoogleError] = useState<string | null>(null)
  const [lookingUpGoogle, setLookingUpGoogle] = useState(false)
  const [selectedCover, setSelectedCover] = useState<BookCoverCandidate | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    let active = true
    void api.books
      .findCoverCandidates(book.title, book.author)
      .then((results) => {
        if (active) setCandidates(results)
      })
      .catch((lookupError: unknown) => {
        if (!active) return
        setCandidates([])
        setError(lookupError instanceof Error ? lookupError.message : 'Failed to find covers.')
      })
    return () => {
      active = false
    }
  }, [book.author, book.title])

  async function findGoogleCovers() {
    setLookingUpGoogle(true)
    setGoogleError(null)
    try {
      setGoogleCandidates(await api.books.findCoverCandidates(book.title, book.author, 'googlebooks'))
    } catch (lookupError: unknown) {
      setGoogleError(lookupError instanceof Error ? lookupError.message : 'Failed to find Google Books covers.')
    } finally {
      setLookingUpGoogle(false)
    }
  }

  async function handleSave() {
    if (!selectedCover) return
    setSaving(true)
    setError(null)

    try {
      const result = await api.books.addBookCover({
        bookId: book.id,
        cover: {
          source: selectedCover.source,
          sourceId: selectedCover.sourceId,
          imageUrl: selectedCover.imageUrl,
        },
      })
      if (!result.coverSaved) {
        setError('This book already has a cover.')
        return
      }
      onSaved()
    } catch (saveError: unknown) {
      setError(saveError instanceof Error ? saveError.message : 'Failed to save cover.')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="book-cover-picker">
      <div>
        <h3 className="modal-title mb-5">Choose a cover</h3>
        <p className="book-detail-author mb-0">
          {book.title} by {book.author}
        </p>
      </div>

      {error ? <div className="alert alert-danger mb-0">{error}</div> : null}
      {candidates === null ? <p className="text-muted mb-0">Finding covers…</p> : null}
      {candidates?.length === 0 ? (
        <p className="text-muted mb-0">No covers were found for this book.</p>
      ) : null}

      {candidates && candidates.length > 0 ? (
        <div className="cover-candidate-grid">
          {[...candidates, ...(googleCandidates ?? [])].map((candidate) => {
            const selected =
              selectedCover?.source === candidate.source &&
              selectedCover.sourceId === candidate.sourceId
            return (
              <button
                key={`${candidate.source}:${candidate.sourceId}`}
                type="button"
                className={`cover-candidate${selected ? ' is-selected' : ''}`}
                onClick={() => setSelectedCover(candidate)}
                aria-pressed={selected}
              >
                <img src={candidate.thumbnailUrl} alt="" />
                <span className="cover-candidate-copy">
                  <strong>{candidate.title}</strong>
                  <span>{candidate.author}</span>
                  <span>{candidate.source === 'openlibrary' ? 'Open Library' : 'Google Books'}</span>
                  {candidate.publicationYear ? <span>{candidate.publicationYear}</span> : null}
                </span>
              </button>
            )
          })}
        </div>
      ) : null}

      {candidates?.[0]?.source === 'openlibrary' && googleCandidates === null ? (
        <button type="button" className="btn" style={{ justifySelf: 'start' }} onClick={() => void findGoogleCovers()} disabled={lookingUpGoogle || saving}>
          {lookingUpGoogle ? 'Searching Google Books...' : 'Search Google Books for more covers'}
        </button>
      ) : null}
      {googleError ? <p className="text-danger mb-0">{googleError}</p> : null}
      {googleCandidates?.length === 0 ? <p className="text-muted mb-0">No additional covers found on Google Books.</p> : null}

      {(googleCandidates?.length || candidates?.[0]?.source === 'googlebooks') ? (
        <p className="cover-attribution mb-0">
          Google Books covers link to their source.{' '}
          <a
            href={(selectedCover?.source === 'googlebooks' ? selectedCover.sourceUrl : null) ?? googleCandidates?.[0]?.sourceUrl ?? candidates?.[0]?.sourceUrl}
            target="_blank"
            rel="noreferrer"
          >
            View on Google Books
          </a>
        </p>
      ) : null}

      <div className="modal-actions">
        <button type="button" className="btn" onClick={onCancel} disabled={saving}>
          Cancel
        </button>
        <button
          type="button"
          className="btn btn-primary"
          onClick={() => void handleSave()}
          disabled={!selectedCover || saving}
        >
          {saving ? 'Saving…' : 'Save cover'}
        </button>
      </div>
    </div>
  )
}

function ReviewItem({
  review,
  onSaved,
}: {
  review: BookReviewDetail
  onSaved: () => void
}) {
  const [editing, setEditing] = useState(false)

  if (!editing) {
    return (
      <article className="book-detail-review">
        <div className="book-detail-review-head">
          <span>{review.dateRead ?? 'Undated'}</span>
          <span className="book-detail-review-head-right">
            <span>{review.rating !== null ? starsFor(review.rating) : '—'}</span>
            <button
              type="button"
              className="btn btn-sm"
              onClick={() => setEditing(true)}
            >
              Edit
            </button>
          </span>
        </div>
        {review.review ? (
          <p className="book-detail-review-body">{review.review}</p>
        ) : (
          <p className="text-muted mb-0">No written review.</p>
        )}
      </article>
    )
  }

  return (
    <ReviewEditor
      review={review}
      onCancel={() => setEditing(false)}
      onSaved={() => {
        setEditing(false)
        onSaved()
      }}
    />
  )
}

function ReviewEditor({
  review,
  onCancel,
  onSaved,
}: {
  review: BookReviewDetail
  onCancel: () => void
  onSaved: () => void
}) {
  const [dateRead, setDateRead] = useState(review.dateRead ?? '')
  const [rating, setRating] = useState<number | null>(review.rating)
  const [text, setText] = useState(review.review ?? '')
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function handleSave() {
    setSaving(true)
    setError(null)
    try {
      await api.books.updateReview({
        reviewId: review.reviewId,
        dateRead: dateRead || null,
        rating,
        review: text.trim() || null,
      })
      onSaved()
    } catch (saveError: unknown) {
      setError(saveError instanceof Error ? saveError.message : 'Failed to save review.')
    } finally {
      setSaving(false)
    }
  }

  return (
    <article className="book-detail-review book-detail-review-editing">
      {error ? <div className="alert alert-danger">{error}</div> : null}
      <div className="review-edit-field">
        <label className="form-label" htmlFor={`date-${review.reviewId}`}>
          Date read
        </label>
        <input
          id={`date-${review.reviewId}`}
          className="form-control"
          type="date"
          value={dateRead}
          onChange={(event) => setDateRead(event.target.value)}
        />
      </div>
      <div className="review-edit-field">
        <label className="form-label">Rating</label>
        <StarRating value={rating} onChange={setRating} />
      </div>
      <div className="review-edit-field">
        <label className="form-label" htmlFor={`review-${review.reviewId}`}>
          Review
        </label>
        <textarea
          id={`review-${review.reviewId}`}
          className="form-control review-textarea"
          value={text}
          onChange={(event) => setText(event.target.value)}
        />
      </div>
      <div className="d-flex justify-content-end gap-10">
        <button
          type="button"
          className="btn btn-sm"
          onClick={onCancel}
          disabled={saving}
        >
          Cancel
        </button>
        <button
          type="button"
          className="btn btn-sm btn-primary"
          onClick={handleSave}
          disabled={saving}
        >
          {saving ? 'Saving…' : 'Save'}
        </button>
      </div>
    </article>
  )
}
