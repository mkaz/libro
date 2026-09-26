import { useEffect, useState } from 'react'

import type { AppSettings, ResultView } from '../shared/types'
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
  { id: 'add', label: 'Add Review' },
]

export function App() {
  const [activeView, setActiveView] = useState<View>('books')
  const [settings, setSettings] = useState<AppSettings | null>(null)
  const [settingsError, setSettingsError] = useState<string | null>(null)
  const [apiKey, setApiKey] = useState('')
  const [keyMessage, setKeyMessage] = useState<string | null>(null)
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    api.app.getSettings().then(setSettings).catch((error: unknown) => {
      setSettingsError(error instanceof Error ? error.message : 'Failed to load settings.')
    })
  }, [])

  async function updateDefaultView(view: ResultView) {
    setSaving(true)
    setSettingsError(null)
    try {
      setSettings(await api.app.setDefaultView(view))
    } catch (error) {
      setSettingsError(error instanceof Error ? error.message : 'Failed to save settings.')
    } finally {
      setSaving(false)
    }
  }

  async function saveGoogleBooksApiKey(key: string) {
    setSaving(true)
    setSettingsError(null)
    setKeyMessage(null)
    try {
      const updated = await api.app.setGoogleBooksApiKey(key)
      setSettings(updated)
      setApiKey('')
      setKeyMessage(key ? 'Google Books API key saved.' : 'Saved key removed.')
    } catch (error) {
      setSettingsError(error instanceof Error ? error.message : 'Failed to save API key.')
    } finally {
      setSaving(false)
    }
  }

  async function chooseDataDirectory() {
    setSaving(true)
    setSettingsError(null)
    try {
      // The main process reloads the window after switching directories.
      await api.app.chooseDataDirectory()
    } catch (error) {
      setSettingsError(error instanceof Error ? error.message : 'Failed to change data directory.')
    } finally {
      setSaving(false)
    }
  }

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

        <details className="settings-menu">
          <summary className="nav-link">Settings</summary>
          <div className="settings-panel">
            <h2 className="settings-title">Settings</h2>
            <div className="settings-field">
              <span className="form-label">Data directory</span>
              <p className="settings-path">{settings?.dataDirectory ?? 'Loading...'}</p>
              <p className="section-copy">Contains libro.db, covers/, and settings.json. Changing directories does not move your data.</p>
              <button
                type="button"
                className="btn btn-secondary"
                disabled={saving || !settings || settings.directoryLocked}
                onClick={() => void chooseDataDirectory()}
              >
                Choose directory…
              </button>
              {settings?.directoryLocked ? (
                <p className="section-copy">The current directory is set by an environment variable or a libro.db in the working directory.</p>
              ) : null}
            </div>
            <div className="settings-field">
              <label className="form-label" htmlFor="defaultView">Default results view</label>
              <select
                id="defaultView"
                className="form-select"
                value={settings?.defaultView ?? 'list'}
                disabled={!settings || saving}
                onChange={(event) => void updateDefaultView(event.target.value as ResultView)}
              >
                <option value="list">List</option>
                <option value="grid">Grid</option>
              </select>
            </div>
            <div className="settings-field">
              <form onSubmit={(event) => { event.preventDefault(); void saveGoogleBooksApiKey(apiKey.trim()) }}>
                <label className="form-label" htmlFor="googleBooksApiKey">Google Books API key</label>
                <input
                  id="googleBooksApiKey"
                  className="form-control"
                  type="password"
                  autoComplete="off"
                  value={apiKey}
                  disabled={!settings || saving}
                  onChange={(event) => { setApiKey(event.target.value); setKeyMessage(null) }}
                  placeholder={settings?.googleBooksApiKeySource ? 'Key configured' : 'Enter API key'}
                />
                <p className="section-copy">
                  {settings?.googleBooksApiKeySource === 'settings'
                    ? 'A key is saved for this data directory. Enter a new key to replace it.'
                    : settings?.googleBooksApiKeySource === 'environment'
                      ? 'Using GOOGLE_BOOKS_API_KEY from your environment. Enter a key to override it.'
                      : 'Enter a key with Books API access to search Google Books.'}
                  {' '}Saved keys are stored in settings.json on this computer.
                </p>
                <div className="d-flex gap-10">
                  <button type="submit" className="btn btn-secondary" disabled={!apiKey.trim() || !settings || saving}>Save key</button>
                  {settings?.googleBooksApiKeySource === 'settings' ? (
                    <button type="button" className="btn" disabled={saving} onClick={() => void saveGoogleBooksApiKey('')}>Remove key</button>
                  ) : null}
                </div>
              </form>
              {keyMessage ? <p className="section-copy" role="status">{keyMessage}</p> : null}
            </div>
            {settingsError ? <p className="alert alert-danger mb-0" role="alert">{settingsError}</p> : null}
          </div>
        </details>
      </header>

      <main className="app-main">
        {activeView === 'books' ? <BooksByYearView defaultView={settings?.defaultView ?? 'list'} /> : null}
        {activeView === 'reports' ? <ReportsView /> : null}
        {activeView === 'search' ? <SearchView defaultView={settings?.defaultView ?? 'list'} /> : null}
        {activeView === 'lists' ? <ListsView /> : null}
        {activeView === 'add' ? <AddBookReviewForm /> : null}
      </main>
    </div>
  )
}
