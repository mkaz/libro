import { useEffect, useState } from 'react'

import type { DbInfo } from '../shared/types'
import { AddBookReviewForm } from './features/add/AddBookReviewForm'
import { BooksByYearView } from './features/books/BooksByYearView'
import { ListsView } from './features/lists/ListsView'
import { ReportsView } from './features/reports/ReportsView'
import { SearchView } from './features/search/SearchView'
import { api } from './lib/api'

type View = 'books' | 'reports' | 'search' | 'lists' | 'add'

const navItems: Array<{ id: View; label: string }> = [
  { id: 'books', label: 'Books' },
  { id: 'reports', label: 'Reports' },
  { id: 'search', label: 'Search' },
  { id: 'lists', label: 'Lists' },
  { id: 'add', label: 'Add Book' },
]

export function App() {
  const [activeView, setActiveView] = useState<View>('books')
  const [dbInfo, setDbInfo] = useState<DbInfo | null>(null)
  const [dbError, setDbError] = useState<string | null>(null)

  useEffect(() => {
    api.app
      .getDbInfo()
      .then(setDbInfo)
      .catch((error: unknown) => {
        setDbError(error instanceof Error ? error.message : 'Failed to load database info.')
      })
  }, [])

  return (
    <div className="app-shell">
      <header className="app-header">
        <h1 className="app-title">Libro</h1>

        <nav className="app-nav" aria-label="Primary navigation">
          {navItems.map((item) => (
            <button
              key={item.id}
              type="button"
              className={`nav-link ${activeView === item.id ? 'is-active' : ''}`}
              onClick={() => setActiveView(item.id)}
            >
              {item.label}
            </button>
          ))}
        </nav>

        <div className="app-status">
          {dbError ? (
            <div className="alert alert-danger mb-0">{dbError}</div>
          ) : (
            <>
              <span className={`badge ${dbInfo?.exists ? 'bg-success' : 'bg-secondary'}`}>
                {dbInfo?.exists ? 'Existing file' : 'Will be created on first write'}
              </span>
              <code className="db-path">{dbInfo?.path ?? 'Resolving database path...'}</code>
            </>
          )}
        </div>
      </header>

      <main className="app-main">
        {activeView === 'books' ? <BooksByYearView /> : null}
        {activeView === 'reports' ? <ReportsView /> : null}
        {activeView === 'search' ? <SearchView /> : null}
        {activeView === 'lists' ? <ListsView /> : null}
        {activeView === 'add' ? <AddBookReviewForm /> : null}
      </main>
    </div>
  )
}
