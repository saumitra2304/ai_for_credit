import { spawnSync } from 'node:child_process'
import { dirname, join, resolve } from 'node:path'
import { existsSync } from 'node:fs'
import { fileURLToPath } from 'node:url'

const here = dirname(fileURLToPath(import.meta.url))
const srcTauri = join(here, '..')
const entitlements = join(srcTauri, 'entitlements.plist')

function sign(target, identifier) {
  const args = [
    '--force',
    '--sign',
    '-',
    '--timestamp=none',
    '--entitlements',
    entitlements,
  ]
  if (identifier) {
    args.push('--identifier', identifier)
  }
  args.push(target)
  const result = spawnSync('codesign', args, { stdio: 'inherit' })
  if (result.status !== 0) {
    process.exit(result.status ?? 1)
  }
}

function findApp() {
  const candidates = []
  if (process.env.CARGO_TARGET_DIR) {
    candidates.push(join(process.env.CARGO_TARGET_DIR, 'release/bundle/macos/Kuber.app'))
  }
  candidates.push(join(srcTauri, 'target/release/bundle/macos/Kuber.app'))
  return candidates.find((path) => existsSync(path))
}

const target = process.argv[2] || findApp()
if (!target) {
  console.error('usage: node sign-macos.mjs <binary-or-app>')
  process.exit(1)
}

const path = resolve(target)
if (!existsSync(path)) {
  console.error(`missing: ${path}`)
  process.exit(1)
}

if (path.endsWith('.app')) {
  const sidecar = join(path, 'Contents/Resources/binaries/reasoning-layer')
  if (existsSync(sidecar)) {
    sign(sidecar, 'com.kuber.reasoning-layer')
  }
  sign(path, 'com.kuber.credit-ai')
} else {
  sign(path, 'com.kuber.reasoning-layer')
}

console.log(`signed ${path}`)
