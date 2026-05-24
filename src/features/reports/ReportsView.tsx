import { useEffect, useState } from 'react'

import type { AuthorCount } from '../../../shared/types'
import { api } from '../../lib/api'

export function ReportsView() {
  const [authorCounts, setAuthorCounts] = useState<AuthorCount[]>([])
  const [minimumBooks, setMinimumBooks] = useState<number | null>(3)
  const [includeUndated, setIncludeUndated] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (minimumBooks === null) {
      setAuthorCounts([])
      return
    }
    void api.reports
      .getAuthorCounts(minimumBooks, includeUndated)
      .then(setAuthorCounts)
      .catch((loadError: unknown) => {
        setError(loadError instanceof Error ? loadError.message : 'Failed to load author report.')
      })
  }, [minimumBooks, includeUndated])

  return (
    <section className="report-grid">
      {error ? <div className="alert alert-danger">{error}</div> : null}

      <article className="card section-card">
        <div className="card-body">
          <div className="section-heading section-heading-inline report-header">
            <div>
              <h2 className="section-title">Author Report</h2>
              <p className="section-copy mb-0">Most-read authors, grouped by count.</p>
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
                  value={minimumBooks ?? ''}
                  onChange={(event) => {
                    const raw = event.target.value
                    setMinimumBooks(raw === '' ? null : Number(raw))
                  }}
                />
              </div>
              <div className="compact-field">
                <label className="form-label">&nbsp;</label>
                <div className="form-check">
                  <input
                    id="includeUndated"
                    className="form-check-input"
                    type="checkbox"
                    checked={includeUndated}
                    onChange={(event) => setIncludeUndated(event.target.checked)}
                  />
                  <label className="form-check-label" htmlFor="includeUndated">
                    Include undated
                  </label>
                </div>
              </div>
            </div>
          </div>

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
        </div>
      </article>
    </section>
  )
}
