import { app, BrowserWindow } from 'electron'
import path from 'node:path'

import { closeDatabase, getDatabase } from './db/client'
import { registerIpcHandlers } from './ipc'

const rendererDevUrl = process.env.VITE_DEV_SERVER_URL ?? 'http://127.0.0.1:5173'

function createWindow(): void {
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
}

app.whenReady().then(() => {
  getDatabase()
  registerIpcHandlers()
  createWindow()

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
