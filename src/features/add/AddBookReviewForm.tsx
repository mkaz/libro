import { useState } from 'react'

import type {
  AddBookReviewInput,
  AddBookReviewResult,
  BookCoverCandidate,
} from '../../../shared/types'
import { api } from '../../lib/api'
import { StarRating } from '../../lib/StarRating'

const initialForm: AddBookReviewInput = {
  title: '',
  author: '',
  pubYear: null,
  pages: null,
  genre: null,
  dateRead: null,
  rating: null,
  review: null,
  cover: null,
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
  const [coverCandidates, setCoverCandidates] = useState<BookCoverCandidate[] | null>(null)
  const [selectedCover, setSelectedCover] = useState<BookCoverCandidate | null>(null)
  const [lookingUpCovers, setLookingUpCovers] = useState(false)
  const [submitting, setSubmitting] = useState(false)

  function resetCoverSelection() {
    setCoverCandidates(null)
    setSelectedCover(null)
  }

  async function findCovers() {
    setLookingUpCovers(true)
    setError(null)
    setResult(null)

    try {
      const candidates = await api.books.findCoverCandidates(form.title, form.author)
      setCoverCandidates(candidates)
    } catch (lookupError: unknown) {
      setCoverCandidates([])
      setError(lookupError instanceof Error ? lookupError.message : 'Failed to find covers.')
    } finally {
      setLookingUpCovers(false)
    }
  }

  async function saveBook(cover: BookCoverCandidate | null) {
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
        cover: cover
          ? { source: cover.source, sourceId: cover.sourceId, imageUrl: cover.imageUrl }
          : null,
      }
      const response = await api.books.addBookReview(payload)
      setResult(response)
      setForm(initialForm)
      resetCoverSelection()
    } catch (submitError: unknown) {
      setError(submitError instanceof Error ? submitError.message : 'Failed to save book.')
    } finally {
      setSubmitting(false)
    }
  }

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (coverCandidates === null) {
      await findCovers()
      return
    }
    if (selectedCover) await saveBook(selectedCover)
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
            {result.coverSaved ? ' Cover saved locally.' : ''}
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
              onChange={(event) => {
                setForm((current) => ({ ...current, title: event.target.value }))
                resetCoverSelection()
              }}
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
              onChange={(event) => {
                setForm((current) => ({ ...current, author: event.target.value }))
                resetCoverSelection()
              }}
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
            <label className="form-label">Rating</label>
            <StarRating
              value={form.rating}
              onChange={(rating) => setForm((current) => ({ ...current, rating }))}
            />
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

          {coverCandidates !== null ? (
            <div className="col-12">
              <div className="cover-confirmation">
                <div>
                  <h3 className="cover-confirmation-title">Choose a cover</h3>
                  <p className="section-copy mb-0">
                    {coverCandidates.length > 0
                      ? `Select one of the ${coverCandidates[0].source === 'openlibrary' ? 'Open Library' : 'Google Books'} covers below.`
                      : 'No covers were found. You can still save the book without one.'}
                  </p>
                </div>

                {coverCandidates.length > 0 ? (
                  <div className="cover-candidate-grid">
                    {coverCandidates.map((candidate) => {
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
                            {candidate.publicationYear ? <span>{candidate.publicationYear}</span> : null}
                          </span>
                        </button>
                      )
                    })}
                  </div>
                ) : null}

                {coverCandidates[0]?.source === 'googlebooks' ? (
                  <p className="cover-attribution mb-0">
                    Cover results provided by Google Books. Each selected result links to its source.
                    {' '}
                    <a href={selectedCover?.sourceUrl ?? coverCandidates[0].sourceUrl} target="_blank" rel="noreferrer">
                      View on Google Books
                    </a>
                  </p>
                ) : null}
              </div>
            </div>
          ) : null}

          <div className="col-12 d-flex justify-content-end gap-10 add-form-buttons">
            {coverCandidates !== null ? (
              <>
                <button
                  type="button"
                  className="btn"
                  onClick={resetCoverSelection}
                  disabled={submitting}
                >
                  Back
                </button>
                <button
                  type="button"
                  className="btn"
                  onClick={() => void saveBook(null)}
                  disabled={submitting}
                >
                  Save without cover
                </button>
                {coverCandidates.length > 0 ? (
                  <button
                    type="submit"
                    className="btn btn-primary"
                    disabled={submitting || selectedCover === null}
                  >
                    {submitting ? 'Saving...' : 'Save selected cover'}
                  </button>
                ) : null}
              </>
            ) : (
              <button type="submit" className="btn btn-primary" disabled={lookingUpCovers}>
                {lookingUpCovers ? 'Finding covers...' : 'Continue to cover'}
              </button>
            )}
          </div>
        </form>
      </div>
    </section>
  )
}
