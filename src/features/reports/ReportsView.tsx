import { useEffect, useState } from 'react'

import type { AuthorCount, ReviewRow } from '../../../shared/types'
import { api } from '../../lib/api'

type ReportView = 'author' | 'rating'

function ReviewTable({ reviews }: { reviews: ReviewRow[] }) {
  if (reviews.length === 0) {
    return <p className="text-muted mb-0">No reviews matched this filter.</p>
  }

  return (
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
            <tr key={review.reviewId}>
              <td>{review.reviewId}</td>
              <td>{review.title}</td>
              <td>{review.author}</td>
              <td>{review.genre ?? 'Unknown'}</td>
              <td>{review.rating ?? 'Unrated'}</td>
              <td>{review.dateRead ?? 'Not set'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export function ReportsView() {
  const [activeReport, setActiveReport] = useState<ReportView>('author')
  const [authorCounts, setAuthorCounts] = useState<AuthorCount[]>([])
  const [ratingReviews, setRatingReviews] = useState<ReviewRow[]>([])
  const [authorReviews, setAuthorReviews] = useState<ReviewRow[]>([])
  const [minimumBooks, setMinimumBooks] = useState(3)
  const [selectedRating, setSelectedRating] = useState<number | ''>(5)
  const [authorFilter, setAuthorFilter] = useState('')
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    void api.reports
      .getAuthorCounts(minimumBooks)
      .then(setAuthorCounts)
      .catch((loadError: unknown) => {
        setError(loadError instanceof Error ? loadError.message : 'Failed to load author report.')
      })
  }, [minimumBooks])

  useEffect(() => {
    void api.reports
      .getReviews(selectedRating === '' ? {} : { rating: selectedRating })
      .then(setRatingReviews)
      .catch((loadError: unknown) => {
        setError(loadError instanceof Error ? loadError.message : 'Failed to load rating report.')
      })
  }, [selectedRating])

  useEffect(() => {
    void api.reports
      .getReviews(authorFilter.trim() ? { author: authorFilter } : {})
      .then((reviews) => setAuthorReviews(reviews.slice(0, 20)))
      .catch((loadError: unknown) => {
        setError(loadError instanceof Error ? loadError.message : 'Failed to load author details.')
      })
  }, [authorFilter])

  return (
    <section className="report-grid">
      {error ? <div className="alert alert-danger">{error}</div> : null}

      <article className="card section-card">
        <div className="card-body">
          <div className="report-menu" role="tablist" aria-label="Report types">
            <button
              type="button"
              className={`report-menu-button ${activeReport === 'author' ? 'is-active' : ''}`}
              onClick={() => setActiveReport('author')}
            >
              Author Report
            </button>
            <button
              type="button"
              className={`report-menu-button ${activeReport === 'rating' ? 'is-active' : ''}`}
              onClick={() => setActiveReport('rating')}
            >
              Rating Report
            </button>
          </div>

          {activeReport === 'author' ? (
            <>
              <div className="section-heading section-heading-inline report-header">
                <div>
                  <h2 className="section-title mb-5">Author Report</h2>
                  <p className="section-copy mb-0">
                    Most-read authors, or search to view books for one author.
                  </p>
                </div>
                <div className="report-author-controls">
                  <div className="compact-field">
                    <label className="form-label" htmlFor="minimumBooks">
                      Minimum books
                    </label>
                    <input
                      id="minimumBooks"
                      className="form-control"
                      inputMode="numeric"
                      value={minimumBooks}
                      onChange={(event) => setMinimumBooks(Number(event.target.value) || 1)}
                    />
                  </div>
                  <div className="report-author-search">
                    <label className="form-label" htmlFor="authorFilter">
                      View by author
                    </label>
                    <input
                      id="authorFilter"
                      className="form-control"
                      placeholder="Start typing an author name"
                      value={authorFilter}
                      onChange={(event) => setAuthorFilter(event.target.value)}
                    />
                  </div>
                </div>
              </div>

              {authorFilter.trim() ? (
                <ReviewTable reviews={authorReviews} />
              ) : (
                <div className="table-responsive">
                  <table className="table align-middle libro-table mb-20">
                    <thead>
                      <tr>
                        <th>Author</th>
                        <th>Books read</th>
                      </tr>
                    </thead>
                    <tbody>
                      {authorCounts.map((author) => (
                        <tr key={author.author}>
                          <td>{author.author}</td>
                          <td>{author.count}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </>
          ) : null}

          {activeReport === 'rating' ? (
            <>
              <div className="section-heading section-heading-inline report-header">
                <div>
                  <h2 className="section-title mb-5">Rating Report</h2>
                  <p className="section-copy mb-0">Filter reviews by score.</p>
                </div>
                <div className="compact-field">
                  <label className="form-label" htmlFor="selectedRating">
                    Rating filter
                  </label>
                  <select
                    id="selectedRating"
                    className="form-select"
                    value={selectedRating}
                    onChange={(event) => {
                      const value = event.target.value
                      setSelectedRating(value ? Number(value) : '')
                    }}
                  >
                    <option value="">All ratings</option>
                    <option value="1">1</option>
                    <option value="2">2</option>
                    <option value="3">3</option>
                    <option value="4">4</option>
                    <option value="5">5</option>
                  </select>
                </div>
              </div>
              <ReviewTable reviews={ratingReviews} />
            </>
          ) : null}
        </div>
      </article>
    </section>
  )
}
