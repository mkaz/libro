import { app, BrowserWindow, dialog, Menu, protocol, shell } from 'electron'
import type { MenuItemConstructorOptions } from 'electron'
import { readFile } from 'node:fs/promises'
import path from 'node:path'

import { getBookCoverPath } from './db/books'
import {
  closeDatabase,
  getCoversDirectory,
  getDatabase,
  getDataDirectory,
  getDbPath,
  isDirectorySelectionLocked,
  writeConfigDbPath,
} from './db/client'
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

    const coverPath = getBookCoverPath(getDatabase(), bookId)
    if (!coverPath) return notFoundResponse()

    const coversDirectory = path.resolve(getCoversDirectory())
    const absoluteCoverPath = path.resolve(getDataDirectory(), coverPath)
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

async function chooseDataDirectory(mainWindow: BrowserWindow): Promise<string | null> {
  if (isDirectorySelectionLocked()) {
    throw new Error('The data directory is set by an environment variable or a libro.db in the current directory.')
  }

  const result = await dialog.showOpenDialog(mainWindow, {
    title: 'Choose Libro Data Directory',
    defaultPath: getDataDirectory(),
    properties: ['openDirectory', 'createDirectory'],
  })
  if (result.canceled || !result.filePaths[0]) return null

  const directory = path.resolve(result.filePaths[0])
  if (directory === getDataDirectory()) return directory

  // A selected directory is used as-is; existing data is never moved or overwritten.
  const previousDbPath = getDbPath()
  closeDatabase()
  try {
    writeConfigDbPath(path.join(directory, 'libro.db'))
    getDatabase()
  } catch (error) {
    closeDatabase()
    writeConfigDbPath(previousDbPath)
    getDatabase()
    throw error
  }
  mainWindow.reload()
  return directory
}

function buildMenu(): void {
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

app.whenReady().then(() => {
  getDatabase()
  registerCoverProtocol()
  registerIpcHandlers(async (sender) => {
    const window = BrowserWindow.fromWebContents(sender)
    if (!window) throw new Error('The application window is no longer available.')
    return chooseDataDirectory(window)
  })
  createWindow()
  buildMenu()

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
