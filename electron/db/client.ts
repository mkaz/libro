import Database from 'better-sqlite3'
import { app } from 'electron'
import { existsSync, mkdirSync } from 'node:fs'
import path from 'node:path'

import { migrateDatabase } from './migrate'

let dbInstance: Database.Database | null = null
let dbPathCache: string | null = null

function resolveDbPath(): string {
  const currentDirDb = path.resolve(process.cwd(), 'libro.db')
  if (existsSync(currentDirDb)) {
    return currentDirDb
  }

  const envDb = process.env.LIBRO_DB
  if (envDb) {
    return envDb
  }

  return path.join(app.getPath('appData'), 'Libro', 'mkaz', 'libro.db')
}

export function getDbPath(): string {
  if (dbPathCache === null) {
    dbPathCache = resolveDbPath()
  }

  return dbPathCache
}

export function getDatabase(): Database.Database {
  if (dbInstance !== null) {
    return dbInstance
  }

  const dbPath = getDbPath()
  mkdirSync(path.dirname(dbPath), { recursive: true })

  const db = new Database(dbPath)
  db.pragma('foreign_keys = ON')
  migrateDatabase(db)

  dbInstance = db
  return db
}

export function getDbInfo() {
  const dbPath = getDbPath()
  return {
    path: dbPath,
    exists: existsSync(dbPath),
  }
}

export function closeDatabase(): void {
  dbInstance?.close()
  dbInstance = null
}
