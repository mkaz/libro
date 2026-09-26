import { app, BrowserWindow, dialog, Menu, protocol, shell } from 'electron'
import type { MenuItemConstructorOptions } from 'electron'
import { readFile } from 'node:fs/promises'
import path from 'node:path'

import { getBookCoverPath } from './db/books'
import { closeDatabase, getDatabase, getDbPath, writeConfigDbPath } from './db/client'
import { registerIpcHandlers } from './ipc'

const rendererDevUrl = process.env.VITE_DEV_SERVER_URL ?? 'http://127.0.0.1:5173'

protocol.registerSchemesAsPrivileged([
  {
    scheme: 'libro-cover',
    privileges: { standard: true, secure: true, supportFetchAPI: true },
  },
])

function notFoundResponse(): Response {
  return new Response('Cover not found.', { status: 404 })
}

function coverContentType(filePath: string): string {
  switch (path.extname(filePath).toLowerCase()) {
    case '.jpg':
    case '.jpeg':
      return 'image/jpeg'
    case '.png':
      return 'image/png'
    case '.webp':
      return 'image/webp'
    default:
      return 'application/octet-stream'
  }
}

function registerCoverProtocol(): void {
  protocol.handle('libro-cover', async (request) => {
    const url = new URL(request.url)
    const bookId = Number(url.pathname.slice(1))
    if (url.hostname !== 'book' || !Number.isInteger(bookId) || bookId <= 0) {
      return notFoundResponse()
    }

    const dbPath = getDbPath()
    const coverPath = getBookCoverPath(getDatabase(), bookId)
    if (!dbPath || !coverPath) return notFoundResponse()

    const coversDirectory = path.resolve(path.dirname(dbPath), 'covers')
    const absoluteCoverPath = path.resolve(path.dirname(dbPath), coverPath)
    if (!absoluteCoverPath.startsWith(`${coversDirectory}${path.sep}`)) {
      return notFoundResponse()
    }

    try {
      const image = await readFile(absoluteCoverPath)
      return new Response(new Uint8Array(image), {
        headers: {
          'Content-Type': coverContentType(absoluteCoverPath),
          'Cache-Control': 'private, max-age=3600',
        },
      })
    } catch {
      return notFoundResponse()
    }
  })
}

async function chooseDatabase(): Promise<string | null> {
  const { response } = await dialog.showMessageBox({
    type: 'question',
    title: 'Select Database',
    message: 'Choose a Libro database',
    detail: 'Open an existing database file or create a new one.',
    buttons: ['Open Existing', 'Create New', 'Cancel'],
    defaultId: 0,
    cancelId: 2,
  })

  if (response === 2) return null

  if (response === 0) {
    const result = await dialog.showOpenDialog({
      title: 'Open Libro Database',
      filters: [{ name: 'SQLite Database', extensions: ['db', 'sqlite', 'sqlite3'] }],
      properties: ['openFile'],
    })
    return result.canceled || result.filePaths.length === 0 ? null : result.filePaths[0]
  }

  // Create new — pick a directory, libro.db will be created inside it
  const result = await dialog.showOpenDialog({
    title: 'Choose Location for New Database',
    properties: ['openDirectory', 'createDirectory'],
  })
  return result.canceled || result.filePaths.length === 0
    ? null
    : path.join(result.filePaths[0], 'libro.db')
}

async function switchDatabase(mainWindow: BrowserWindow): Promise<void> {
  const dbPath = await chooseDatabase()
  if (!dbPath) return

  writeConfigDbPath(dbPath)
  closeDatabase()
  getDatabase()
  mainWindow.reload()
}

function buildMenu(mainWindow: BrowserWindow): void {
  const template: MenuItemConstructorOptions[] = [
    {
      label: app.name,
      submenu: [
        { role: 'about' },
        { type: 'separator' },
        { role: 'services' },
        { type: 'separator' },
        { role: 'hide' },
        { role: 'hideOthers' },
        { role: 'unhide' },
        { type: 'separator' },
        { role: 'quit' },
      ],
    },
    {
      label: 'File',
      submenu: [
        {
          label: 'Open Database...',
          accelerator: 'CmdOrCtrl+O',
          click: () => switchDatabase(mainWindow),
        },
      ],
    },
    { role: 'editMenu' },
    { role: 'viewMenu' },
    { role: 'windowMenu' },
  ]

  Menu.setApplicationMenu(Menu.buildFromTemplate(template))
}

function createWindow(): BrowserWindow {
  const mainWindow = new BrowserWindow({
    width: 1440,
    height: 940,
    minWidth: 1100,
    minHeight: 760,
    backgroundColor: '#111827',
    title: 'Libro Desktop',
    webPreferences: {
      preload: path.join(__dirname, 'preload.cjs'),
      contextIsolation: true,
      nodeIntegration: false,
    },
  })

  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    if (url.startsWith('https://')) void shell.openExternal(url)
    return { action: 'deny' }
  })

  if (app.isPackaged) {
    mainWindow.loadFile(path.resolve(__dirname, '../dist/index.html'))
  } else {
    const loadDevUrl = () => {
      mainWindow.loadURL(rendererDevUrl).catch(() => {
        // Dev server may not be ready yet; retry shortly.
        setTimeout(loadDevUrl, 300)
      })
    }
    mainWindow.webContents.on('did-fail-load', () => {
      setTimeout(loadDevUrl, 300)
    })
    loadDevUrl()
    mainWindow.webContents.openDevTools({ mode: 'detach' })
  }

  return mainWindow
}

app.whenReady().then(async () => {
  if (getDbPath() === null) {
    const dbPath = await chooseDatabase()
    if (!dbPath) {
      app.quit()
      return
    }
    writeConfigDbPath(dbPath)
    closeDatabase() // reset cache so getDatabase() re-reads fresh config
  }

  getDatabase()
  registerCoverProtocol()
  registerIpcHandlers()
  const mainWindow = createWindow()
  buildMenu(mainWindow)

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow()
    }
  })
})

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

app.on('before-quit', () => {
  closeDatabase()
})
