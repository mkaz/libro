import { app, BrowserWindow, dialog, Menu } from 'electron'
import type { MenuItemConstructorOptions } from 'electron'
import path from 'node:path'

import { closeDatabase, getDatabase, getDbPath, writeConfigDbPath } from './db/client'
import { registerIpcHandlers } from './ipc'

const rendererDevUrl = process.env.VITE_DEV_SERVER_URL ?? 'http://127.0.0.1:5173'

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

  if (app.isPackaged) {
    mainWindow.loadFile(path.resolve(__dirname, '../dist/index.html'))
  } else {
    mainWindow.loadURL(rendererDevUrl)
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
