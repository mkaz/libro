import { spawn } from 'node:child_process'
import path from 'node:path'
import process from 'node:process'

function usage() {
  console.log('Usage: npm run dev [-- --db <database-path>]')
}

function parseDatabasePath(args) {
  let databasePath = null

  for (let index = 0; index < args.length; index += 1) {
    const argument = args[index]

    if (argument === '--help' || argument === '-h') {
      usage()
      process.exit(0)
    }

    if (argument === '--db') {
      const value = args[index + 1]
      if (!value || value.startsWith('--')) {
        throw new Error('--db requires a database path.')
      }
      databasePath = value
      index += 1
      continue
    }

    if (argument.startsWith('--db=')) {
      databasePath = argument.slice('--db='.length)
      if (!databasePath) throw new Error('--db requires a database path.')
      continue
    }

    throw new Error(`Unknown option: ${argument}`)
  }

  return databasePath ? path.resolve(databasePath) : null
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
  const databasePath = parseDatabasePath(process.argv.slice(2))
  const env = { ...process.env }

  if (databasePath) {
    env.LIBRO_DB_OVERRIDE = databasePath
    console.log(`Using development database: ${databasePath}`)
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
