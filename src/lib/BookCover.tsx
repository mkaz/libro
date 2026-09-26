import { useEffect, useState } from 'react'

function bookCoverUrl(bookId: number): string {
  return `libro-cover://book/${bookId}`
}

export function BookCover({
  bookId,
  title,
  hasCover,
  className = '',
}: {
  bookId: number
  title: string
  hasCover: boolean
  className?: string
}) {
  const [imageFailed, setImageFailed] = useState(false)

  useEffect(() => {
    setImageFailed(false)
  }, [bookId, hasCover])

  if (!hasCover || imageFailed) {
    return (
      <div
        className={`book-cover-placeholder ${className}`.trim()}
        role="img"
        aria-label={`No cover available for ${title}`}
      >
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" />
          <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2Z" />
        </svg>
        <span>No cover</span>
      </div>
    )
  }

  return (
    <img
      className={`book-cover-image ${className}`.trim()}
      src={bookCoverUrl(bookId)}
      alt={`Cover of ${title}`}
      onError={() => setImageFailed(true)}
    />
  )
}
