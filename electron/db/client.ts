import Database from 'better-sqlite3'
import { app } from 'electron'
import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs'
import path from 'node:path'

import { migrateDatabase } from './migrate'

let dbInstance: Database.Database | null = null
let dbPathCache: string | undefined

function getConfigPath(): string {
  return path.join(app.getPath('userData'), 'libro-config.json')
}

interface StorageConfig {
  dataDirectory?: string
  databaseFilename?: string
  dbPath?: string
}

function readConfigDbPath(): string | null {
  const configPath = getConfigPath()
  if (!existsSync(configPath)) return null
  try {
    const config = JSON.parse(readFileSync(configPath, 'utf8')) as StorageConfig
    if (config.dataDirectory) {
      return path.join(
        path.resolve(config.dataDirectory),
        path.basename(config.databaseFilename ?? 'libro.db'),
      )
    }
    return config.dbPath ? path.resolve(config.dbPath) : null
  } catch {
    return null
  }
}

export function writeConfigDbPath(dbPath: string): void {
  const absoluteDbPath = path.resolve(dbPath)
  const config: StorageConfig = {
    dataDirectory: path.dirname(absoluteDbPath),
    databaseFilename: path.basename(absoluteDbPath),
  }
  mkdirSync(path.dirname(getConfigPath()), { recursive: true })
  writeFileSync(getConfigPath(), JSON.stringify(config, null, 2))
}

function dbPathIn(directory: string): string {
  return path.join(path.resolve(directory), 'libro.db')
}

function resolveDbPath(): string {
  const overrideDirectory = process.env.LIBRO_DATA_DIR_OVERRIDE
  if (overrideDirectory) return dbPathIn(overrideDirectory)

  // Keep the database-path overrides for compatibility with existing workflows.
  const overrideDb = process.env.LIBRO_DB_OVERRIDE
  if (overrideDb) return path.resolve(overrideDb)

  const currentDirDb = path.resolve(process.cwd(), 'libro.db')
  if (existsSync(currentDirDb)) return currentDirDb

  const envDirectory = process.env.LIBRO_DATA_DIR
  if (envDirectory) return dbPathIn(envDirectory)

  const envDb = process.env.LIBRO_DB
  if (envDb) return path.resolve(envDb)

  return readConfigDbPath() ?? dbPathIn(app.getPath('userData'))
}

export function getDbPath(): string {
  dbPathCache ??= resolveDbPath()
  return dbPathCache
}

export function getDataDirectory(): string {
  return path.dirname(getDbPath())
}

export function getCoversDirectory(): string {
  return path.join(getDataDirectory(), 'covers')
}

export function getDatabase(): Database.Database {
  if (dbInstance !== null) {
    return dbInstance
  }

  const dbPath = getDbPath()
  mkdirSync(getCoversDirectory(), { recursive: true })

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
  dbPathCache = undefined
}
