import { spawn } from 'node:child_process'
import path from 'node:path'
import process from 'node:process'

function usage() {
  console.log('Usage: npm run dev [-- --data-dir <directory> | --db <database-path>]')
}

function parseStoragePath(args) {
  let storagePath = null

  for (let index = 0; index < args.length; index += 1) {
    const argument = args[index]

    if (argument === '--help' || argument === '-h') {
      usage()
      process.exit(0)
    }

    if (argument === '--data-dir') {
      const value = args[index + 1]
      if (!value || value.startsWith('--')) {
        throw new Error('--data-dir requires a directory.')
      }
      storagePath = { type: 'directory', path: value }
      index += 1
      continue
    }

    if (argument.startsWith('--data-dir=')) {
      const value = argument.slice('--data-dir='.length)
      if (!value) throw new Error('--data-dir requires a directory.')
      storagePath = { type: 'directory', path: value }
      continue
    }

    if (argument === '--db') {
      const value = args[index + 1]
      if (!value || value.startsWith('--')) {
        throw new Error('--db requires a database path.')
      }
      storagePath = { type: 'database', path: value }
      index += 1
      continue
    }

    if (argument.startsWith('--db=')) {
      const value = argument.slice('--db='.length)
      if (!value) throw new Error('--db requires a database path.')
      storagePath = { type: 'database', path: value }
      continue
    }

    throw new Error(`Unknown option: ${argument}`)
  }

  return storagePath ? { ...storagePath, path: path.resolve(storagePath.path) } : null
}

function run(command, args, env = process.env) {
  return new Promise((resolve, reject) => {
    const child = spawn(command, args, { env, stdio: 'inherit' })
    child.once('error', reject)
    child.once('exit', (code, signal) => {
      if (signal) {
        reject(new Error(`${command} stopped with ${signal}.`))
      } else if (code !== 0) {
        reject(new Error(`${command} exited with code ${code}.`))
      } else {
        resolve()
      }
    })
  })
}

async function main() {
  const storagePath = parseStoragePath(process.argv.slice(2))
  const env = { ...process.env }

  if (storagePath?.type === 'directory') {
    env.LIBRO_DATA_DIR_OVERRIDE = storagePath.path
    console.log(`Using development data directory: ${storagePath.path}`)
  } else if (storagePath) {
    env.LIBRO_DB_OVERRIDE = storagePath.path
    console.log(`Using development database: ${storagePath.path}`)
  }

  await run('npm', ['run', 'build:electron'], env)
  await run(
    'concurrently',
    [
      '-k',
      'vite',
      'wait-on http://127.0.0.1:5173 && electron dist-electron/main.cjs',
    ],
    env,
  )
}

main().catch((error) => {
  console.error(error instanceof Error ? error.message : error)
  process.exitCode = 1
})
