import { readFileSync, writeFileSync, existsSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'

const here = dirname(fileURLToPath(import.meta.url))
const srcTauri = join(here, '..')
const repo = join(srcTauri, '../..')

function parseEnv(path) {
  if (!existsSync(path)) return {}
  const out = {}
  for (const line of readFileSync(path, 'utf8').split(/\r?\n/)) {
    const trimmed = line.trim()
    if (!trimmed || trimmed.startsWith('#')) continue
    const eq = trimmed.indexOf('=')
    if (eq <= 0) continue
    out[trimmed.slice(0, eq)] = trimmed.slice(eq + 1)
  }
  return out
}

const merged = {
  ...parseEnv(join(repo, 'reasoning_layer/.env')),
  ...parseEnv(join(repo, '.env')),
}
delete merged.mongo_url

const lines = Object.entries(merged).map(([key, value]) => `${key}=${value}`)
writeFileSync(join(srcTauri, 'bundled.env'), `${lines.join('\n')}\n`)
console.log(`wrote bundled.env (${lines.length} keys)`)
