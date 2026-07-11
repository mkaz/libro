import { useEffect, useState } from 'react'

import type { BookDetail } from '../../shared/types'
import { api } from './api'
import { starsFor } from './ratings'

export function BookDetailModal({
  bookId,
  onClose,
}: {
  bookId: number
  onClose: () => void
}) {
  const [book, setBook] = useState<BookDetail | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    void api.books
      .getBookDetail(bookId)
      .then(setBook)
      .catch((loadError: unknown) => {
        setError(loadError instanceof Error ? loadError.message : 'Failed to load book.')
      })
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
                  <article key={review.reviewId} className="book-detail-review">
                    <div className="book-detail-review-head">
                      <span>{review.dateRead ?? 'Undated'}</span>
                      <span>
                        {review.rating !== null ? starsFor(review.rating) : '—'}
                      </span>
                    </div>
                    {review.review ? (
                      <p className="book-detail-review-body">{review.review}</p>
                    ) : (
                      <p className="text-muted mb-0">No written review.</p>
                    )}
                  </article>
                ))}
              </div>
            )}
          </>
        ) : null}
      </div>
    </div>
  )
}
