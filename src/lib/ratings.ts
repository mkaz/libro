export function starsFor(rating: number): string {
  return '★'.repeat(rating) + '☆'.repeat(5 - rating)
}
