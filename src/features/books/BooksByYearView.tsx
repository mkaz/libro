import { useEffect, useState } from 'react'

import type { ReviewRow, YearCount } from '../../../shared/types'
import { api } from '../../lib/api'

function buildYearOptions(yearCounts: YearCount[]): number[] {
  const currentYear = new Date().getFullYear()
  const years = yearCounts
    .map((entry) => Number(entry.year))
    .filter((year) => !Number.isNaN(year))

  if (!years.includes(currentYear)) {
    years.push(currentYear)
  }

  return [...new Set(years)].sort((left, right) => right - left)
}

export function BooksByYearView() {
  const [yearCounts, setYearCounts] = useState<YearCount[]>([])
  const [selectedYear, setSelectedYear] = useState(new Date().getFullYear())
  const [reviews, setReviews] = useState<ReviewRow[]>([])
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    void api.reports
      .getYearCounts()
      .then(setYearCounts)
      .catch((loadError: unknown) => {
        setError(loadError instanceof Error ? loadError.message : 'Failed to load years.')
      })
  }, [])

  useEffect(() => {
    void api.reports
      .getReviews({ year: selectedYear })
      .then(setReviews)
      .catch((loadError: unknown) => {
        setError(loadError instanceof Error ? loadError.message : 'Failed to load books for year.')
      })
  }, [selectedYear])

  const years = buildYearOptions(yearCounts)
  const selectedCount =
    yearCounts.find((entry) => Number(entry.year) === selectedYear)?.count ?? reviews.length

  return (
    <section className="content-stack">
      {error ? <div className="alert alert-danger">{error}</div> : null}

      <article className="card section-card">
        <div className="card-body">
          <div className="section-heading section-heading-inline books-toolbar">
            <div className="books-toolbar-main">
              <h2 className="section-title books-title mb-0">Books Read</h2>
              <p className="section-copy books-count mb-0">
                {selectedCount} {selectedCount === 1 ? 'book' : 'books'} in {selectedYear}.
              </p>
            </div>
            <div className="compact-field books-year-field">
              <label className="form-label" htmlFor="booksYear">
                Year
              </label>
              <select
                id="booksYear"
                className="form-select"
                value={selectedYear}
                onChange={(event) => setSelectedYear(Number(event.target.value))}
              >
                {years.map((year) => (
                  <option key={year} value={year}>
                    {year} ({yearCounts.find((entry) => Number(entry.year) === year)?.count ?? 0})
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>
      </article>

      <article className="card section-card">
        <div className="card-body">
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
                {reviews.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="table-empty-state">
                      No books read in {selectedYear}.
                    </td>
                  </tr>
                ) : (
                  reviews.map((review) => (
                    <tr key={review.reviewId}>
                      <td>{review.reviewId}</td>
                      <td>{review.title}</td>
                      <td>{review.author}</td>
                      <td>{review.genre ?? 'Unknown'}</td>
                      <td>{review.rating ?? 'Unrated'}</td>
                      <td>{review.dateRead ?? 'Not set'}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </article>
    </section>
  )
}
