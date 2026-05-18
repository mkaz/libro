import Database from 'better-sqlite3'
import { app } from 'electron'
import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs'
import path from 'node:path'

import { migrateDatabase } from './migrate'

let dbInstance: Database.Database | null = null
let dbPathCache: string | null | undefined = undefined

function getConfigPath(): string {
  return path.join(app.getPath('userData'), 'libro-config.json')
}

function readConfigDbPath(): string | null {
  const configPath = getConfigPath()
  if (!existsSync(configPath)) return null
  try {
    const config = JSON.parse(readFileSync(configPath, 'utf8')) as { dbPath?: string }
    return config.dbPath ?? null
  } catch {
    return null
  }
}

export function writeConfigDbPath(dbPath: string): void {
  writeFileSync(getConfigPath(), JSON.stringify({ dbPath }, null, 2))
}

function resolveDbPath(): string | null {
  const currentDirDb = path.resolve(process.cwd(), 'libro.db')
  if (existsSync(currentDirDb)) {
    return currentDirDb
  }

  const envDb = process.env.LIBRO_DB
  if (envDb) {
    return envDb
  }

  return readConfigDbPath()
}

export function getDbPath(): string | null {
  if (dbPathCache === undefined) {
    dbPathCache = resolveDbPath()
  }
  return dbPathCache
}

export function getDatabase(): Database.Database {
  if (dbInstance !== null) {
    return dbInstance
  }

  const dbPath = getDbPath()
  if (!dbPath) {
    throw new Error('No database path configured.')
  }

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
    path: dbPath ?? '',
    exists: dbPath ? existsSync(dbPath) : false,
  }
}

export function closeDatabase(): void {
  dbInstance?.close()
  dbInstance = null
  dbPathCache = undefined
}
