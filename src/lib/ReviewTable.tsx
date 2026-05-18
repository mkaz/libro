import type { ReviewRow } from '../../shared/types'
import { starsFor } from './ratings'

export function ReviewTable({
  reviews,
  emptyMessage = 'No reviews found.',
}: {
  reviews: ReviewRow[]
  emptyMessage?: string
}) {
  if (reviews.length === 0) {
    return <p className="text-muted mb-0">{emptyMessage}</p>
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
              <td>{review.genre ?? '—'}</td>
              <td>{review.rating !== null ? starsFor(review.rating) : '—'}</td>
              <td>{review.dateRead ?? '—'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
