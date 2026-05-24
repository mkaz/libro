import { useEffect, useState } from 'react'

import type { ReviewRow } from '../../../shared/types'
import { api } from '../../lib/api'
import { ReviewTable } from '../../lib/ReviewTable'

export function SearchView() {
  const [reviews, setReviews] = useState<ReviewRow[]>([])
  const [authorFilter, setAuthorFilter] = useState('')
  const [selectedRating, setSelectedRating] = useState<number | ''>('')
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const filters = {
      ...(authorFilter.trim() ? { author: authorFilter } : {}),
      ...(selectedRating !== '' ? { rating: selectedRating } : {}),
    }
    void api.reports
      .getReviews(filters)
      .then(setReviews)
      .catch((loadError: unknown) => {
        setError(loadError instanceof Error ? loadError.message : 'Failed to load reviews.')
      })
  }, [authorFilter, selectedRating])

  return (
    <section className="report-grid">
      {error ? <div className="alert alert-danger">{error}</div> : null}

      <article className="card section-card">
        <div className="card-body">
          <div className="section-heading section-heading-inline report-header">
            <div>
              <h2 className="section-title">Search</h2>
              <p className="section-copy mb-0">Filter reviews by author or rating.</p>
            </div>
            <div className="search-controls">
              <div className="report-author-search">
                <label className="form-label" htmlFor="authorFilter">
                  Author
                </label>
                <input
                  id="authorFilter"
                  className="form-control"
                  placeholder="Start typing an author name"
                  value={authorFilter}
                  onChange={(event) => setAuthorFilter(event.target.value)}
                />
              </div>
              <div className="compact-field">
                <label className="form-label" htmlFor="selectedRating">
                  Rating
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
          </div>
          <ReviewTable reviews={reviews} />
        </div>
      </article>
    </section>
  )
}
