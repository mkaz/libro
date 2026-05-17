import { useState } from 'react'

import type { AddBookReviewInput, AddBookReviewResult } from '../../../shared/types'
import { api } from '../../lib/api'

const initialForm: AddBookReviewInput = {
  title: '',
  author: '',
  pubYear: null,
  pages: null,
  genre: null,
  dateRead: null,
  rating: null,
  review: null,
}

function toOptionalNumber(value: string): number | null {
  if (!value.trim()) {
    return null
  }

  return Number(value)
}

export function AddBookReviewForm() {
  const [form, setForm] = useState(initialForm)
  const [result, setResult] = useState<AddBookReviewResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setSubmitting(true)
    setError(null)
    setResult(null)

    try {
      const payload = {
        ...form,
        title: form.title.trim(),
        author: form.author.trim(),
        genre: form.genre?.trim() || null,
        review: form.review?.trim() || null,
      }
      const response = await api.books.addBookReview(payload)
      setResult(response)
      setForm(initialForm)
    } catch (submitError: unknown) {
      setError(submitError instanceof Error ? submitError.message : 'Failed to save book.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <section className="card section-card add-form-card">
      <div className="card-body">
        <div className="section-heading">
          <div>
            <h2 className="section-title mb-5">Add Book and Review</h2>
            <p className="section-copy mb-0">
              This matches the CLI&apos;s main add command. If the book already exists by title and
              author, the app attaches a new review instead of creating a duplicate book.
            </p>
          </div>
        </div>

        {result ? (
          <div className="alert alert-success">
            Saved review <strong>#{result.reviewId}</strong> for book <strong>#{result.bookId}</strong>
            . {result.usedExistingBook ? 'Existing book reused.' : 'New book created.'}
          </div>
        ) : null}

        {error ? <div className="alert alert-danger">{error}</div> : null}

        <form className="row g-20" onSubmit={handleSubmit}>
          <div className="col-12 col-xl-6">
            <label className="form-label" htmlFor="title">
              Title
            </label>
            <input
              id="title"
              className="form-control"
              value={form.title}
              onChange={(event) => setForm((current) => ({ ...current, title: event.target.value }))}
              required
            />
          </div>

          <div className="col-12 col-xl-6">
            <label className="form-label" htmlFor="author">
              Author
            </label>
            <input
              id="author"
              className="form-control"
              value={form.author}
              onChange={(event) => setForm((current) => ({ ...current, author: event.target.value }))}
              required
            />
          </div>

          <div className="col-12 col-md-4">
            <label className="form-label" htmlFor="pubYear">
              Publication year
            </label>
            <input
              id="pubYear"
              className="form-control"
              inputMode="numeric"
              value={form.pubYear ?? ''}
              onChange={(event) =>
                setForm((current) => ({ ...current, pubYear: toOptionalNumber(event.target.value) }))
              }
            />
          </div>

          <div className="col-12 col-md-4">
            <label className="form-label" htmlFor="pages">
              Pages
            </label>
            <input
              id="pages"
              className="form-control"
              inputMode="numeric"
              value={form.pages ?? ''}
              onChange={(event) =>
                setForm((current) => ({ ...current, pages: toOptionalNumber(event.target.value) }))
              }
            />
          </div>

          <div className="col-12 col-md-4">
            <label className="form-label" htmlFor="genre">
              Genre
            </label>
            <input
              id="genre"
              className="form-control"
              value={form.genre ?? ''}
              onChange={(event) => setForm((current) => ({ ...current, genre: event.target.value }))}
            />
          </div>

          <div className="col-12 col-md-6">
            <label className="form-label" htmlFor="dateRead">
              Date read
            </label>
            <input
              id="dateRead"
              className="form-control"
              type="date"
              value={form.dateRead ?? ''}
              onChange={(event) =>
                setForm((current) => ({ ...current, dateRead: event.target.value || null }))
              }
            />
          </div>

          <div className="col-12 col-md-6">
            <label className="form-label" htmlFor="rating">
              Rating
            </label>
            <select
              id="rating"
              className="form-select"
              value={form.rating ?? ''}
              onChange={(event) =>
                setForm((current) => ({ ...current, rating: toOptionalNumber(event.target.value) }))
              }
            >
              <option value="">Unrated</option>
              <option value="1">1</option>
              <option value="2">2</option>
              <option value="3">3</option>
              <option value="4">4</option>
              <option value="5">5</option>
            </select>
          </div>

          <div className="col-12">
            <label className="form-label" htmlFor="review">
              Review
            </label>
            <textarea
              id="review"
              className="form-control review-textarea"
              value={form.review ?? ''}
              onChange={(event) => setForm((current) => ({ ...current, review: event.target.value }))}
            />
          </div>

          <div className="col-12 d-flex justify-content-end gap-10 add-form-buttons">
<button type="submit" className="btn btn-primary" disabled={submitting}>
              {submitting ? 'Saving...' : 'Save book and review'}
            </button>
          </div>
        </form>
      </div>
    </section>
  )
}
