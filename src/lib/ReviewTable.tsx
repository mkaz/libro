import { useState } from 'react'

import type { ResultView, ReviewRow } from '../../shared/types'
import { BookCover } from './BookCover'
import { BookDetailModal } from './BookDetailModal'
import { starsFor } from './ratings'
import { ViewToggle } from './ViewToggle'

export function ReviewTable({
  reviews,
  emptyMessage = 'No reviews found.',
  defaultView = 'list',
}: {
  reviews: ReviewRow[]
  emptyMessage?: string
  defaultView?: ResultView
}) {
  const [selectedBookId, setSelectedBookId] = useState<number | null>(null)
  const [resultView, setResultView] = useState<ResultView>(defaultView)
  const [booksWithNewCovers, setBooksWithNewCovers] = useState<Set<number>>(() => new Set())

  if (reviews.length === 0) {
    return <p className="text-muted mb-0">{emptyMessage}</p>
  }

  return (
    <>
      <div className="results-view-toolbar">
        <ViewToggle value={resultView} onChange={setResultView} />
      </div>

      {resultView === 'list' ? (
        <div className="table-responsive">
          <table className="table align-middle libro-table">
            <thead>
              <tr>
                <th>Review ID</th>
                <th>Title</th>
                <th>Author</th>
                <th>Genre</th>
                <th>Rating</th>
                <th>Date Read</th>
              </tr>
            </thead>
            <tbody>
              {reviews.map((review) => (
                <tr
                  key={review.reviewId}
                  className="libro-row-clickable"
                  onClick={() => setSelectedBookId(review.bookId)}
                  tabIndex={0}
                  role="button"
                  onKeyDown={(event) => {
                    if (event.key === 'Enter' || event.key === ' ') {
                      event.preventDefault()
                      setSelectedBookId(review.bookId)
                    }
                  }}
                >
                  <td>{review.reviewId}</td>
                  <td>{review.title}</td>
                  <td>{review.author}</td>
                  <td>{review.genre ?? '—'}</td>
                  <td>{review.rating !== null ? starsFor(review.rating) : '—'}</td>
                  <td>{review.dateRead ?? '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="book-result-grid">
          {reviews.map((review) => (
            <button
              key={review.reviewId}
              type="button"
              className="book-result-card"
              onClick={() => setSelectedBookId(review.bookId)}
            >
              <BookCover
                bookId={review.bookId}
                title={review.title}
                hasCover={review.hasCover || booksWithNewCovers.has(review.bookId)}
                className="book-result-cover"
              />
              <span className="book-result-copy">
                <strong className="book-result-title">{review.title}</strong>
                <span className="book-result-author">{review.author}</span>
                <span className="book-result-meta">
                  <span>{review.rating !== null ? starsFor(review.rating) : 'Unrated'}</span>
                  <span>{review.dateRead ?? 'Undated'}</span>
                </span>
              </span>
            </button>
          ))}
        </div>
      )}

      {selectedBookId !== null ? (
        <BookDetailModal
          bookId={selectedBookId}
          onClose={() => setSelectedBookId(null)}
          onCoverSaved={() => {
            setBooksWithNewCovers((current) => new Set(current).add(selectedBookId))
          }}
        />
      ) : null}
    </>
  )
}
