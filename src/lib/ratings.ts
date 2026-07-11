export function starsFor(rating: number): string {
  const full = Math.floor(rating)
  const hasHalf = rating - full >= 0.5
  const empty = 5 - full - (hasHalf ? 1 : 0)
  return '★'.repeat(full) + (hasHalf ? '½' : '') + '☆'.repeat(empty)
}
