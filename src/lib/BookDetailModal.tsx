import { useEffect, useState } from 'react'

import type { BookDetail, BookReviewDetail } from '../../shared/types'
import { api } from './api'
import { starsFor } from './ratings'
import { StarRating } from './StarRating'

export function BookDetailModal({
  bookId,
  onClose,
}: {
  bookId: number
  onClose: () => void
}) {
  const [book, setBook] = useState<BookDetail | null>(null)
  const [error, setError] = useState<string | null>(null)

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
        onClose()
      }
    }
    window.addEventListener('keydown', handleKey)
    return () => window.removeEventListener('keydown', handleKey)
  }, [onClose])

  return (
    <div className="modal-overlay" onClick={onClose} role="dialog" aria-modal="true">
      <div
        className="modal-box modal-box-wide"
        onClick={(e) => e.stopPropagation()}
      >
        {error ? <div className="alert alert-danger">{error}</div> : null}
        {!book && !error ? <p className="text-muted mb-0">Loading…</p> : null}
        {book ? (
          <>
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
