import { useState } from 'react'

export function StarRating({
  value,
  onChange,
}: {
  value: number | null
  onChange: (value: number | null) => void
}) {
  const [hover, setHover] = useState<number | null>(null)
  const display = hover ?? value ?? 0

  function fillFor(star: number): 'full' | 'half' | 'empty' {
    if (display >= star) {
      return 'full'
    }
    if (display >= star - 0.5) {
      return 'half'
    }
    return 'empty'
  }

  return (
    <div className="star-rating">
      <div
        className="star-rating-stars"
        onMouseLeave={() => setHover(null)}
        role="radiogroup"
        aria-label="Rating"
      >
        {[1, 2, 3, 4, 5].map((star) => {
          const fill = fillFor(star)
          return (
            <span key={star} className="star-rating-star">
              <button
                type="button"
                className="star-rating-zone star-rating-left"
                onMouseEnter={() => setHover(star - 0.5)}
                onClick={() => onChange(star - 0.5)}
                aria-label={`${star - 0.5} stars`}
              />
              <button
                type="button"
                className="star-rating-zone star-rating-right"
                onMouseEnter={() => setHover(star)}
                onClick={() => onChange(star)}
                aria-label={`${star} stars`}
              />
              <span className={`star-rating-glyph star-rating-${fill}`} aria-hidden="true">
                <span className="star-rating-bg">★</span>
                <span className="star-rating-fg">★</span>
              </span>
            </span>
          )
        })}
      </div>
      <button
        type="button"
        className="star-rating-clear btn btn-sm"
        onClick={() => onChange(null)}
        disabled={value === null}
      >
        Clear
      </button>
    </div>
  )
}
