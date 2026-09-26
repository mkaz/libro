import type { ResultView } from '../../shared/types'

export function ViewToggle({
  value,
  onChange,
}: {
  value: ResultView
  onChange: (view: ResultView) => void
}) {
  return (
    <div className="view-toggle" role="group" aria-label="Results view">
      <button
        type="button"
        className={`view-toggle-button${value === 'list' ? ' is-active' : ''}`}
        onClick={() => onChange('list')}
        aria-label="List view"
        aria-pressed={value === 'list'}
        title="List view"
      >
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path d="M8 6h13M8 12h13M8 18h13" />
          <path d="M3 6h.01M3 12h.01M3 18h.01" />
        </svg>
      </button>
      <button
        type="button"
        className={`view-toggle-button${value === 'grid' ? ' is-active' : ''}`}
        onClick={() => onChange('grid')}
        aria-label="Grid view"
        aria-pressed={value === 'grid'}
        title="Grid view"
      >
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <rect x="3" y="3" width="7" height="7" />
          <rect x="14" y="3" width="7" height="7" />
          <rect x="3" y="14" width="7" height="7" />
          <rect x="14" y="14" width="7" height="7" />
        </svg>
      </button>
    </div>
  )
}
